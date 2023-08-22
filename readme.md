# Seams detection TMB

## Introduction

This repository provides a solution for detecting seams in H-beams during operations at TMB. 
The solution is built upon convolutional neural networks, with a specific emphasis on utilizing 
YOLOv5 as the backbone network responsible for extracting high-level features from the input image.


## Repository Structure

The repository is organized as follows:

- `_dev_features/`: in development features
- `ShadowStarter/`: C# application to keep alive MSC and H-engine running in production
- `Training/`: all the python scripts for training, this is a clone from the original Yolov5 from ultralytics
- - `ManifestGenerator.py`: in-house addition to Yolov5 in order to generate the yaml file needed by Yolo describing the dataset and classes
- `Viewer/`: all the code to run *H-Beam Processor* and *H-engine* in production

The following diagram shows the interaction between *H-Beam Processor* and *H-engine in Production*:

![H-Beam processor and Viewer](_readme/hengine_flow.drawio.png)

### H-Beam Processor

This application is designed for testing the models after training. It also supports the display of CVAT 1.0 and Yolo 1.1 annotations.

![H-Beam processor and Viewer](_readme/hbeam.PNG)

### H-engine for production



## Getting Started

To begin using the tools provided in this repository, follow these steps:

1. Clone the repository to your local machine.

2. Execute Viewer/main.py to start H-Beam processor. Alternative you could start the application by executing Viewer/HBeamProcessor.bat but you might need to configure the location of your python enviroment.

3. Execute Viewer/production.py. Alternative you could start the application by executing Viewer/HBeamProcessor.bat but you might need to configure the location of your python enviroment.

Example of `production.bat` to start up the H-engine in production mode:

```bash
@echo OFF

SETLOCAL EnableDelayedExpansion

SET CONDA=D:\__TMB_SeamsReleases\env\seams
SET LOCATION=D:\__TMB_SeamsReleases\H_Processor
SET PATH=%CONDA%\Scripts;%CONDA%;%PATH%

CALL activate base
START python production.py

@echo ON
```

## Database Credentials

Databases:

For the `trucks` database:

```python
trucks = SDMExtraction(
    host='8CC1340PY2',      # where the database is stored
    port=3306,              # port
    user='trucks',          # user
    pwd='Trucks2023.',      # user password
    db='truckdensity',      # name of the database
    path='data',            # folder to save extracted data
    prefix='Trucks',        # prefix for extracted files
    code='CODE_PROD',       # column name for production code
    flag='Trucks'           # Rails or Trucks >> according the extraction you need
)
```

For the `rails` database:

```python
rails = SDMExtraction(
    host='8CC12827T8',        # where the database is stored
    port=3306,                # port
    user='rails',             # user
    pwd='Rails2023.',         # user password
    db='raildensity',         # name of the database
    path='data',              # folder to save extracted data
    prefix='Rails',           # prefix for extracted files
    code='CODPROP1',          # column name for production code
    flag='Rails'              # Rails or Trucks >> according the extraction you need
)
```

The databases, Trucks and Rails, are both hosted as local MySQL databases and are accessed using the following credentials:


## Computers Credentials

### New and currently working computers:

| PC type         | PC Name    | IP Address    | User                 | Password       |
|-----------------|------------|---------------|----------------------|----------------|
| Trucks SDM-di   | 8CC1340PY2 | 10.25.104.87  | EUROPE\AMLPLSCRAP    | AM@acierie01*  |
| Rails SDM-di    | 8CC12827T8 | 10.25.110.201 | EUROPE\AMLPLSCRAP    | AM@acierie01*  |
| Differdange SSM | 8CC1482L6B | DHCP          | EUROPE\AMLPLSCRAP    | AM@acierie01*  |
| Belval SSM      | 8CC0460KW8 | 10.28.101.97  | profilarbed\gracsoft | AM@acierie01*  |
| Delphi PC       | 8CC3141STT | DHCP          | EUROPE\AMLPLSCRAP    | AM@acierie01*  |

- Differdange SSM is still under development, the software is not completely revamped. Currently, at Jaime's office.

- Delphi PC is an Elite desktop HP with Delphi 10.4 installed in order to modify the delphi applications. Currently, at Jaime's office.

### Old computers:

| PC type         | Status                               | PC Name                       | User                  | Password      |
|-----------------|--------------------------------------|-------------------------------|-----------------------|---------------|
| Trucks SDM      | in Differdange, still in the network | W09321                        | profilarbed\DIACSDM   | AMdipwd**     |
| Rails SDM       | Jaime's office, down in a shelf      | W08994                        | W08994\Admin          | 1Qlari-fari   |
| Differdange SSM | an Azure VM  and running in prod!    | VMDiscr01-SSM (139.53.211.76) | profilarbed\gracsoft  | AM@acierie01* |
| Belval SSM      | Lost between IP and Belval           | CZC4194DP6                    | profilarbed\gracsoft  | AM@acierie01* |

## Flowcharts

### SDM Differdange

Trucks and Rails are retrieving SAP data by querying an FTP listing for each incoming truck and wagon-rail.

![SDM device flow](_readme/SDM_flow.png)

### SSM Belval

![SDM device flow](_readme/SSM_belval.png)

## Feedback and Support

If you have any questions, suggestions, or issues related to the SDM Data Extraction, [open an issue](https://github.com/your-username/sdm-data-extraction/issues) in this repository.