# STIR
Web scraping with Selenium and ProxyMesh, storing the data in MongoDB

## Technologies Used:
1. Selenium
2. MongoDB
3. ProxyMesh
4. HTML
5. Python-Dotenv
6. Flask

### Installation
Clone the repository to your local machine:

```bash
git clone https://github.com/akash-dewangan03/STIR.git
```
Navigate to the project directory:

```bash
cd STIR
```
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```
Set up your environment variables by creating a .env file in the project directory and adding the necessary credentials:

```makefile
proxymesh_user
proxymesh_pass
twitter_email
twitter_user
twitter_pass
mongodb_uri

```
Usage
Run the Flask application:

```bash
python app.py
```
Open your web browser and go to http://localhost:5000 to access the web interface.
