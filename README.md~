cli-ec2-allow-pub-ip
====================

CLI tools to add public IP to AWS Security Groups

Use Boto python library https://github.com/boto/boto
##Why
This tool let you (temporary) add your public IP to a EC2 security group, for many TCP ports (for now, no need for UDP but it will easy to add).
Then you can just do your stuff, and simply revoke thoses rights and restore the previous state.

I use it to let me quickly configure the EC2 group when I have to connect to my instance from various places : home (my ISP don't give me a fixed IP adress), hotel...

##Usage
First, install Boto
```
sudo pip install boto
```
then configure you AWS secret key in ~/.boto or something else (see http://docs.pythonboto.org/en/latest/boto_config_tut.html)
and finally just launch 
```
$ add-ec2-ip.py -h
```

Basically, 
*select a Security Group name and a list of TCP ports to open as program parameters
*start the program
*rules will be addedd
*then the program will hang on a "PRESS A KEY TO CONTINUE" message
*When you are done, just press ENTER and the rules will be revoked

###Dry Run
A "--dry" option exists: rules won't be created nor revoked. It let you check your settings (keys..) and the group name.
##Example
```
$ ./add-ec2-ip.py -g test_group  22 80 443 8080
Args :: Group :  test_group , TCP ports:  [22, 80, 443, 8080]
Connected to EC2Connection:ec2.eu-west-1.amazonaws.com
Security groups:  1  found:  [SecurityGroup:test_group]
Targeted Security Group:  test_group
1 instances will be affected
  -> EC2 Instance:  i-xxxxx ec2-xxx-xxx-xxx-xxx.eu-west-1.compute.amazonaws.com running m1.medium  started at 2012-10-10T02:15:13.000Z
Current public IP: yyy.yyy.yyy.yyy (retrieved by  http://agentgatech.appspot.com/ )
1 rules actually defined in test_group
IPPermissions:tcp(9090-9090)
           AUTH   >>  yyy.yyy.yyy.yyy/32 , TCP:  22
           AUTH   >>  yyy.yyy.yyy.yyy/32 , TCP:  80
           AUTH   >>  yyy.yyy.yyy.yyy/32 , TCP:  443
           AUTH   >>  yyy.yyy.yyy.yyy/32 , TCP:  8080
Now,  5 rules defined in test_group
=========================================================
=========== PRESS A KEY TO REVOKE RULES =================
=========================================================
2012-10-30 00:23:13.674065

Duration: 0:00:04.983607
           REVOKE  >>  yyy.yyy.yyy.yyy/32 , TCP:  22
           REVOKE  >>  yyy.yyy.yyy.yyy/32 , TCP:  80
           REVOKE  >>  yyy.yyy.yyy.yyy/32 , TCP:  443  
           REVOKE  >>  yyy.yyy.yyy.yyy/32 , TCP:  8080
Now,  1 rules defined in test_group
```
