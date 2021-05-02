# test_dev

### Setup made as per the below requirements:

1 VPN Server setup in frankfurt Location 

2 Application Load Balancer
- NGINX server
- Ubuntu server with installed nginx
- Part of “Auto scaling group” (min: 2, max:2)

3 Classic Load Balancer
- APP server
- Ubuntu server with installed node.js
- Part of “Auto scaling group” (min: 2, max:3)

4.3 DB servers
- Servers are available in 3 different availability zones
- MongoDB replica set
- Only accessible from APP servers and via VPN

All infrastructure deployed with Terraform and AWS cloud platform

![image](https://user-images.githubusercontent.com/54053423/116818133-5af6f200-ab87-11eb-81b7-46b8ffe31b05.png)

Command used to run the services 

Enter into terraform afetr connecting into VPN server 

Keep all the files fromm git hub and execute below commands it will run "main.tf"

$ cd terraform

$terraform init  (intitalize backend)

$terraform plan  (Preliminary check it create resource using aws cloud and prepare setup to run, Plan: 1 to add should be expect at the end )

$terraform apply 

Enter a value: yes

terraform.tf.state will be created in JSON format 

Completed 


