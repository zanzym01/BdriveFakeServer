# BDRIVE FAKE SERVER

Patch and launch fake server for netdrive3 and/or cloudsync [netdrive.net](http://www.netdrive.net/) [cloudsync.bdrive.com](https://cloudsync.bdrive.com/)

***Note: Please buy app if you can.***
# User manual:
- Install Netdrive and/or CloudSync
- Download the content of dist folder
- Patch exe files by running in a cmd console:
  - **For NetDrive:** ```BdriveFakeServer.exe -n <netDrive install folder path>```
  - **For CloudSync:** ```BdriveFakeServer.exe -c <cloudSync install folder path>```
- Install fake server as a service by running **installService.bat** (remove the service by running **removeService.bat**)
- You can also launch the fake server manually by running **BdriveFakeServer.exe** before executing NetDrive or CloudSync.
- To have more details, run ```BdriveFakeServer.exe -h``` in a cmd window

***Note: Application requires Admin privileges***
