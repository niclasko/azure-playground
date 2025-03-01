# Parameters
param(
    [string]$envName = "azure_playground_env",  # Name of the Conda environment
    [string]$requirementsFile = "./requirements.txt",  # Path to requirements.txt
    [string]$pythonVersion = "3.11"  # Desired Python version
)

# Function to check if Conda is installed
function Check-CondaInstalled {
    if (-not (Get-Command "conda" -ErrorAction SilentlyContinue)) {
        Write-Error "Conda is not installed or not in PATH. Please install Conda and try again."
        exit 1
    }
}

# Function to filter requirements file
function Filter-RequirementsFile {
    param (
        [string]$inputFile
    )

    $tempFile = [System.IO.Path]::GetTempFileName()

    try {
        Get-Content $inputFile | Where-Object { -not ($_ -match "^-e\s|^#") } | Set-Content $tempFile
    } catch {
        Write-Error "Failed to filter requirements file: $_"
        exit 1
    }

    return $tempFile
}

# Function to install dependencies
function Install-Dependencies {
    param (
        [string]$envName,
        [string]$requirementsFile
    )

    $filteredRequirements = Filter-RequirementsFile -inputFile $requirementsFile

    try {
        Get-Content $filteredRequirements | ForEach-Object {
            $package = $_.Trim()
            if (-not [string]::IsNullOrWhiteSpace($package)) {
                Write-Host "Installing package: $package" -ForegroundColor Cyan
                conda install -n $envName $package -y -q 2> $null

                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "Package '$package' not found in Conda. Attempting to install with pip..."
                    conda run -n $envName pip install $package
                }
            }
        }
    } catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    } finally {
        # Clean up temporary file
        Remove-Item $filteredRequirements -Force
    }
}

# Function to install editable packages
function Install-EditablePackages {
    param (
        [string]$envName,
        [string]$requirementsFile
    )

    $editablePackages = Get-Content $requirementsFile | Where-Object { $_ -match "^-e\s" -and -not ($_ -match "^#") }

    if ($editablePackages) {
        Write-Host "Installing editable packages..." -ForegroundColor Cyan
        foreach ($line in $editablePackages) {
            $packagePath = $line -replace "^-e\s", ""
            Write-Host "Installing editable package from path: $packagePath" -ForegroundColor Green
            conda run -n $envName pip install -e $packagePath
        }
    } else {
        Write-Host "No editable packages found in requirements.txt." -ForegroundColor Yellow
    }
}

# Function to create a Conda environment
function Create-CondaEnvironment {
    param (
        [string]$envName,
        [string]$requirementsFile,
        [string]$pythonVersion
    )

    Write-Host "Checking if environment '$envName' already exists..." -ForegroundColor Yellow
    $envs = conda env list | Select-String $envName

    if ($envs) {
        Write-Host "Environment '$envName' already exists. Skipping creation." -ForegroundColor Cyan
    } else {
        Write-Host "Creating Conda environment '$envName' with Python $pythonVersion..." -ForegroundColor Green
        conda create --name $envName python=$pythonVersion -y
    }

    # Install dependencies
    if (Test-Path $requirementsFile) {
        Write-Host "Installing dependencies from '$requirementsFile'..." -ForegroundColor Green
        Install-Dependencies -envName $envName -requirementsFile $requirementsFile
        Install-EditablePackages -envName $envName -requirementsFile $requirementsFile
    } else {
        Write-Warning "Requirements file '$requirementsFile' not found. Skipping dependency installation."
    }

    Write-Host "Conda environment setup complete!" -ForegroundColor Green
}

function Setup-NotebookCleaner {
    conda run -n $envName pip install nbstripout pre-commit
    nbstripout --install
    pre-commit install
}

function Extra-Installs {
    python -m spacy download en_core_web_sm  # Download spaCy model
}

# Main script logic
Check-CondaInstalled
Create-CondaEnvironment -envName $envName -requirementsFile $requirementsFile -pythonVersion $pythonVersion
Setup-NotebookCleaner
Extra-Installs