provider "aws"{
	region = "eu-central-1"
	access_key = "your_key"
	secret_key = "your_key"
}

resource "aws_instance" "ec2"{
	ami = "ami-0767046d1677be5a0"
	insatnce_type = "t2.micro"
	key_name = "ansible_frkf_key"
	security_groups = ["ansible-SG"]
	tags = {
		Name = "Ansible"
	}
	
	provisioner "local-exec" {
		command = "sleep 120; ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --private-key /home/usant/ansible_frkf_key.pem -i ${aws_instance.ec2.public_ip}, playbook.yaml"
	}
}

