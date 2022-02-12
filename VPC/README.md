![cover.png](https://github.com/gulywwx/aws_lab/blob/main/VPC/vpc.png)

# VPC Demo

**For a public subnet to have Internet access, inbound and outbound, an account needs:**
 - Internet Gateway attached to a VPC
 - route to the Internet Gateway in the attached route table
 - Instances have public IP addresses (auto-assigned or attached Elastic IP address)
 - Appropriate security group and NACL allowances



**For a private subnet to have Internet access, the following will provide outbound Internet access but not inbound:**
 - Internet Gateway attached to a VPC
 - NAT Gateway or Instance in a public subnet in the same VPC
 - Route to the NAT Gateway or Instance in the private subnet’s attached route table
 - Appropriate security group and NACL allowances

