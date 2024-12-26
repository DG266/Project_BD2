# Rumors
A very basic microblogging platform.

## Features
You can create an account, log into your account, log out of your account. You can create posts, edit them or delete them. 

## Installation and Running
First and foremost, download Python (I've used Python 3.10.6 and PyCharm), Git (you'll probably need Git LFS to download the datasets) and MongoDB.
Now, follow these steps:
1. Clone this repository by running `git clone https://github.com/DG266/Rumors.git`.
2. Go inside the `Rumors` folder.
3. Install all the requirements by running `pip install -r requirements.txt`.
4. Start MongoDB.
5. Run `flask init-db`, this will load the data inside the database.
6. Run `app.py`.
   
At this point, you should be fine: open your favourite browser and visit `http://127.0.0.1:5000/` (or `http://localhost:5000/`).

## Datasets
COVID19 Tweets: https://www.kaggle.com/datasets/gpreda/covid19-tweets

Russo-Ukrainian War Tweets: https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows
