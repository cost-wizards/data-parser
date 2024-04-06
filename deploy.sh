
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 471112948871.dkr.ecr.us-east-1.amazonaws.com

docker build --platform linux/amd64 -t 471112948871.dkr.ecr.us-east-1.amazonaws.com/data-parser:latest .

docker push 471112948871.dkr.ecr.us-east-1.amazonaws.com/data-parser:latest

# aws lambda update-function-code --function-name data-parser--image-uri 471112948871.dkr.ecr.us-east-1.amazonaws.com/data-parser:latest

