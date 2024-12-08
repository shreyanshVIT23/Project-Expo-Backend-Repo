# **Project Expo - Backend Repository** 🚀  

This repository contains the **Python-based backend** for the **Project Expo** platform. The backend handles core functionalities, including API endpoints and the SVG generation logic.

---

## **📖 Table of Contents**

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Technologies Used](#-technologies-used)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
  - [Testing the Code](#testing-the-code)
- [Contributing](#-contributing)
- [Contact](#-contact)

---

## **📝 About the Project**

The **Project Expo Backend** is a Python-based solution designed to handle server-side tasks, including **user navigation preferences** (e.g., "Lift" or "Stairs") and **SVG output generation**. This repository serves as the backend counterpart to the broader Project Expo application.

---

## **✨ Features**

- API endpoints for navigation preferences
- SVG output generation
- Customizable options for starting and ending points
- Lightweight and scalable Python backend

---

## **💻 Technologies Used**

- **Programming Language**: Python
- **Frameworks**: Flask 
- **Testing**: Manual
- **Other Tools**: Add additional tools used in the backend

---

## **🚀 Getting Started**

Follow these steps to set up and run the backend locally.

### **Prerequisites**

- Python 3.7+ installed
- Git installed
- Basic knowledge of Python and APIs

### **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shreyanshVIT23/Project-Expo-Backend-Repo.git
   ```
2. **Go to file dir**:
   ```bash
   cd Project-Expo-Backend-Repo
   ```
3. **Run the Code**:
   ```bash
   python .\server_startup.py
   ```
     
### **Running the Application**
 To run the code run the following in server dir
 ```bash
  cd server
  flask run
 ```
---
## **Testing the Code**

### **Testing the shortest path algorithm**
1. **After Setup go to server and test the code (example)**:
    ```bash
    cd server
    python .\Test\run_test.py 230 Stairs Stairs --open
    ```
2. **Now change accordingly**:
   - 'T004' with the start point you want
   - '507' as the endpoint
   - 'Lift' or 'Stairs' as preference.
   - Also you can add ```
     --open``` as suffix to open the the output file in your default browser

### **Testing the Chatbot Audio Feature**
1. **After Setup first run the application**
   ```bash
   cd .\server
   flask run
   ```
   
2. **Now run imitation frontend normally**
   - Now open a new terminal tab and run the code below
   - ```bash
      cd .\server\Test\
      python .\imitation_frontend_test.py
      ```
   - *Note: That the code will record your microphone for 9 seconds and will give output in result. To check if the name of teacher was matched go to flask terminal*
---
## **🤝 Contributing**
Contributions are welcome! Here's how you can contribute:

Fork this repository.
Create a new branch:
```bash
git checkout -b feature-name
```
Make your changes and commit:
```bash
git commit -m "Add feature description"
```
Push to your branch:
```bash
git push origin feature-name
```
Open a Pull Request.

---

## **📧 Contact**
For any queries or suggestions, feel free to reach out:
- Author: Shreyansh
- GitHub: shreyanshVIT23
- Linkedin: https://www.linkedin.com/in/shreyansh-pande-04713728a/
