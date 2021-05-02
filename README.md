# test_dev


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
