# Baldrick
Baldrick is a simple tool that launches various steps. It is intended as a follow up after a nmap/nessus/openvas scan and 
add validation to these reports. It will be able to do the following:
- validate
...It will run additional tools as validations for found ports. E.g. when SSL has been found, sslyze/testssl/sslscan can 
be run against the found port.
- bruteforce
...When services are found it will attempt to brute force the credentials based on provided user/password lists
- exploit
...It can run various exploits 

## Options
The following options will be supported:
```
  -h      --help          This screen
  -n FILE --nessus  FILE  The nessus report which is used as a based
  -m FILE --nmap    FILE  The XML nmap output 
  -o FILE --openvas FILE  The openvas XML report
  -v      --validate      Run the validation plugins
  -b      --brute         Run the brute force plugins, this requires the following two options --uid and --pwd
          --uid     FILE  The file containing credentials
          --pwd     FILE  The file containing passwords
  -e      --exploit       Run the exploit plugins
  ```
