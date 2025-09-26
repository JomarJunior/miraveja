# Use Node LTS image
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose development server port
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]
