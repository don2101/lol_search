from flask import Flask, render_template, request
import os
import requests
import json
from bs4 import BeautifulSoup as BS

app = Flask(__name__, template_folder='views')

@app.route("/")
def index() :
    return render_template('index.html')


@app.route('/search')
def search() :
    userName = request.args.get('userName')
    
    # 1. search data in op.gg
    #   - sending a request to op.gg,
    #   - html from op.gg
    baseUrl = 'http://www.op.gg/summoner/userName='
    response = requests.get(baseUrl + userName)

    # 2. pull wins and loses information
    doc = BS(response.text)
    
    wins = doc.select_one('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > \
    div.SideContent > div.TierBox.Box > div.SummonerRatingMedium > div.TierRankInfo > \
    div.TierInfo > span.WinLose > span.wins').text
    wins = int(wins[:-1:])
    
    loses = doc.select_one('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > \
    div.SideContent > div.TierBox.Box > div.SummonerRatingMedium > div.TierRankInfo > \
    div.TierInfo > span.WinLose > span.losses').text
    
    loses = int(loses[:-1:])
    
    KEY=os.getenv('RIOT_API_KEY')
    
    infoUrl = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(userName, KEY)
    userInfo = requests.get(infoUrl).json()
    
    userNick = userInfo.get('name')
    encryptedId = userInfo.get('id')
    
    
    spectatorUrl = "https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{}?api_key={}".format(encryptedId, KEY)
    spectatorResult = requests.get(spectatorUrl).json()
    
    
    inGame = ""
    
    if(spectatorResult.get('gameId') == None) :
        inGame = "게임중이 아닙니다."
    else :
        inGame = "게임중입니다."
    
    winRate = round((wins*100)/(wins+loses), 3)
    
    return render_template('search.html', user=userNick, wins=wins, loses=loses, winRate=winRate, inGame=inGame)
