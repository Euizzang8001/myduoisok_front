import streamlit as st
import requests
from datetime import datetime
import json
import os
from PIL import Image
import io
import pandas as pd

back_url = st.secrets["BACK_URL"]

get_puuid_url = back_url + '/get-puuid'
get_match_list_url = back_url + '/get-matchid'
get_match_info_url = back_url + '/get-matchinfo'
check_match_in_db_url = back_url + '/check-match-in-db'
append_match_info_url = back_url + '/append-matchinfo'

image_url = 'https://ddragon.leagueoflegends.com/cdn/14.13.1/img/champion/'


champion_data = requests.get('https://ddragon.leagueoflegends.com/cdn/14.13.1/data/en_US/champion.json').json()

number_list = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']

st.title('My Duo Is OK..? :frowning:')
    
explain1 = '누군가와 함께 롤을 플레이하는 소환사들이 참 많습니다.'
explain2 = '같이 하는 게임에서 누가 범인인지, 누가 캐리하는지 궁금하신 적 있으시죠?'
explain3 = 'My duo is ok와 함께라면 더 재밌게 플레이 할 수 있을겁니다:rainbow:'
st.write(explain1)
st.write(explain2)
st.write(explain3)
# summoner = st.text_input('Write The Summoner Name(Without Tag and Seperate Summoner Names with Commas)')
summoner = st.text_input("검색하고 싶은 소환사들의 소환사명과 태그를 쓰세요!")
st.write("','로 구분하세요 ex) 거모동의자랑#KR1, 순대꼬치#KR1, 필요할사람#KR1")
search_summoner = st.button('Search')

summoner_puuid_list = []

match_id_list = []

if search_summoner: #검색하기 위해 버튼을 누르면 검색 정보를 db에 저장하고 불러오기
    summoner_nospace = ''.join(i for i in summoner if not i.isspace())
    summoner_list = list(summoner_nospace.split(','))
    st.write(f':man_and_woman_holding_hands:{summoner}:woman_and_man_holding_hands: Your Matches Are Here!')
    for summoner_name_and_tagline in summoner_list:
        get_per_summoner_puuid_url = get_puuid_url + summoner_name_and_tagline
        summoner_puuid = requests.get(get_per_summoner_puuid_url, params={'summoner_and_tagline': summoner_name_and_tagline}).json()
        summoner_puuid_list.append(summoner_puuid)
        if len(match_id_list) == 0:
            match_id_list = requests.get(get_match_list_url, params={'summoner_puuid': summoner_puuid}).json()
        else:
            match_id_list = list(set(match_id_list) & set(requests.get(get_match_list_url, params={'summoner_puuid': summoner_puuid}).json()))
    if len(match_id_list) == 0 or match_id_list[0] == 0 or match_id_list[0] == '0':
        # st.error('Are You Duo? No game You Played Together In Last 100 Games !!')
        st.error('듀오가 맞습니까???? 최근 100게임 중 소환사의 협곡을 한판도 같이 플레이 하지 않았습니다!!')
    else:
        # st.write(f"Out of 100 games, We Played Together in {len(match_id_list)}!!")
        st.write(f"100게임 중 {len(match_id_list)}판을 같이 하셨네요!!")
        match_id_list = sorted(match_id_list, reverse=False)
        for match_number in range(len(match_id_list)-1, -1, -1):
            match = match_id_list[match_number]
            # st.write(match)
            goldSum = {}
            teamBluePick = []
            teamRedPick = []
            #db에 있는지 확인하고
            match_in_db = requests.get(check_match_in_db_url, params={'match_id': match}).json()
            if not match_in_db:
                #정보 라이엇으로부터 가져오고
                match_info = requests.get(get_match_info_url, params={'match_id': match}).json()
                if match_info['info']['gameMode'] != 'CLASSIC':
                    continue
                same_lane_enemy = {}
                riotIdGameName_list = []
                riotIdTagline_list = []
                for i in range(10):
                    lane_str = match_info['info']['participants'][i]['teamPosition']
                    if lane_str == 'TOP':
                        lane = 0
                    elif lane_str == 'JUNGLE':
                        lane = 1
                    elif lane_str == 'MIDDLE':
                        lane = 2
                    elif lane_str == 'BOTTOM':
                        lane = 3
                    else:
                        lane = 4
                    if lane not in same_lane_enemy:
                        same_lane_enemy[lane] = []
                        same_lane_enemy[lane].extend([match_info['info']['participants'][i]['assists'],
                                                match_info['info']['participants'][i]['champLevel'],
                                                match_info['info']['participants'][i]['deaths'],
                                                match_info['info']['participants'][i]['goldEarned'],
                                                match_info['info']['participants'][i]['kills'],
                                                match_info['info']['participants'][i]['totalDamageDealtToChampions'],
                                                match_info['info']['participants'][i]['totalDamageTaken'],
                                                match_info['info']['participants'][i]['totalHeal'],
                                                match_info['info']['participants'][i]['totalTimeCCDealt'],
                                                match_info['info']['participants'][i]['visionScore']
                                                ])
                    else:
                        same_lane_enemy[lane][0] -= match_info['info']['participants'][i]['assists']
                        same_lane_enemy[lane][1] -= match_info['info']['participants'][i]['champLevel']
                        same_lane_enemy[lane][2] -= match_info['info']['participants'][i]['deaths']
                        same_lane_enemy[lane][3] -= match_info['info']['participants'][i]['goldEarned']
                        same_lane_enemy[lane][4] -= match_info['info']['participants'][i]['kills']
                        same_lane_enemy[lane][5] -= match_info['info']['participants'][i]['totalDamageDealtToChampions']
                        same_lane_enemy[lane][6] -= match_info['info']['participants'][i]['totalDamageTaken']
                        same_lane_enemy[lane][7] -= match_info['info']['participants'][i]['totalHeal']
                        same_lane_enemy[lane][8] -= match_info['info']['participants'][i]['totalTimeCCDealt']
                        same_lane_enemy[lane][9] -= match_info['info']['participants'][i]['visionScore']

                for i in range(10):
                    lane_str = match_info['info']['participants'][i]['teamPosition']    
                    if lane_str == 'TOP':
                        lane = 0
                    elif lane_str == 'JUNGLE':
                        lane = 1
                    elif lane_str == 'MIDDLE':
                        lane = 2
                    elif lane_str == 'BOTTOM':
                        lane = 3
                    else:
                        lane = 4
                    # if 'riotIdGameName' in match_info['info']['participants'][i] or len(match_info['info']['participants'][i]['riotIdGameName']) != 0:
                    if 'riotIdGameName' in match_info['info']['participants'][i]:
                        riotIdGameName = match_info['info']['participants'][i]['riotIdGameName']
                    else: 
                        riotIdGameName = match_info['info']['participants'][i]['summonerName']
                    riotIdGameName_list.append(riotIdGameName)
                    # if 'riotIdTagline' in match_info['info']['participants'][i] or len(match_info['info']['participants'][i]['riotIdTagline']) != 0:
                    if 'riotIdTagline' in match_info['info']['participants'][i]:    
                        riotIdTagline = match_info['info']['participants'][i]['riotIdTagline']
                    else: 
                        riotIdTagline = 'KR1'
                    riotIdTagline_list.append(riotIdTagline)
                    if i < 5:
                        per_summoner_info = {
                            "matchId": match,
                            "assists": match_info['info']['participants'][i]['assists'],
                            "champLevel": match_info['info']['participants'][i]['champLevel'],
                            "championId": match_info['info']['participants'][i]['championId'],
                            "championName": match_info['info']['participants'][i]['championName'],
                            "deaths": match_info['info']['participants'][i]['deaths'],
                            "goldEarned": match_info['info']['participants'][i]['goldEarned'],
                            "goldSpent": match_info['info']['participants'][i]['goldSpent'],
                            "kills": match_info['info']['participants'][i]['kills'],
                            "lane": match_info['info']['participants'][i]['teamPosition'],
                            "summonerName": match_info['info']['participants'][i]['summonerName'],
                            "riotIdGameName":  riotIdGameName_list[i],
                            "riotIdTagline":  riotIdTagline_list[i],
                            "role": match_info['info']['participants'][i]['role'],
                            "teamId": match_info['info']['participants'][i]['teamId'],
                            "totalDamageDealtToChampions":match_info['info']['participants'][i]['totalDamageDealtToChampions'],
                            "totalDamageTaken": match_info['info']['participants'][i]['totalDamageTaken'],
                            "totalHeal": match_info['info']['participants'][i]['totalHeal'],
                            "totalTimeCCDealt": match_info['info']['participants'][i]['totalTimeCCDealt'],
                            "win": match_info['info']['participants'][i]['win'],
                            "visionScore": match_info['info']['participants'][i]['visionScore'],

                            "versusassists": same_lane_enemy[lane][0],
                            "versuschampionLevel" :same_lane_enemy[lane][1],
                            "versusdeaths":same_lane_enemy[lane][2],
                            "versusgoldEarned":same_lane_enemy[lane][3],
                            "versuskills":same_lane_enemy[lane][4],
                            "versusTDDTC":same_lane_enemy[lane][5],
                            "versusTDT" : same_lane_enemy[lane][6],
                            "versusTH":same_lane_enemy[lane][7],
                            "versusTTCCD":same_lane_enemy[lane][8],
                            "versusVS": same_lane_enemy[lane][9],
                        }
                        teamBluePick.append(per_summoner_info['championId'])
                    else:
                        per_summoner_info = {
                            "matchId": match,
                            "assists": match_info['info']['participants'][i]['assists'],
                            "champLevel": match_info['info']['participants'][i]['champLevel'],
                            "championId": match_info['info']['participants'][i]['championId'],
                            "championName": match_info['info']['participants'][i]['championName'],
                            "deaths": match_info['info']['participants'][i]['deaths'],
                            "goldEarned": match_info['info']['participants'][i]['goldEarned'],
                            "goldSpent": match_info['info']['participants'][i]['goldSpent'],
                            "kills": match_info['info']['participants'][i]['kills'],
                            "lane": match_info['info']['participants'][i]['teamPosition'],
                            "summonerName": match_info['info']['participants'][i]['summonerName'],
                            "riotIdGameName":  riotIdGameName_list[i],
                            "riotIdTagline":  riotIdTagline_list[i],
                            "role": match_info['info']['participants'][i]['role'],
                            "teamId": match_info['info']['participants'][i]['teamId'],
                            "totalDamageDealtToChampions":match_info['info']['participants'][i]['totalDamageDealtToChampions'],
                            "totalDamageTaken": match_info['info']['participants'][i]['totalDamageTaken'],
                            "totalHeal": match_info['info']['participants'][i]['totalHeal'],
                            "totalTimeCCDealt": match_info['info']['participants'][i]['totalTimeCCDealt'],
                            "win": match_info['info']['participants'][i]['win'],
                            "visionScore": match_info['info']['participants'][i]['visionScore'],

                            "versusassists": -same_lane_enemy[lane][0],
                            "versuschampionLevel":-same_lane_enemy[lane][1],
                            "versusdeaths":-same_lane_enemy[lane][2],
                            "versusgoldEarned":-same_lane_enemy[lane][3],
                            "versuskills":-same_lane_enemy[lane][4],
                            "versusTDDTC":-same_lane_enemy[lane][5],
                            "versusTDT" : -same_lane_enemy[lane][6],
                            "versusTH":-same_lane_enemy[lane][7],
                            "versusTTCCD":-same_lane_enemy[lane][8],
                            "versusVS": -same_lane_enemy[lane][9],
                        }
                        teamRedPick.append(per_summoner_info['championId'])
                    if per_summoner_info['teamId'] not in goldSum:
                        goldSum[per_summoner_info['teamId']] = 0
                    goldSum[per_summoner_info['teamId']] += per_summoner_info['goldEarned']
                    append_summoner_info_url = back_url + f"/append-summonerinfo/{match_info['metadata']['participants'][i]}"
                    result = requests.put(append_summoner_info_url, params={'puuid': match_info['metadata']['participants'][i]},  json=per_summoner_info)
                #db에 저장하고
                per_match_info = {
                    "gameMode": match_info['info']['gameMode'],
                    'matchId':  match,
                    "gameDuration": match_info['info']['gameDuration'],
                    "gameCreation": match_info['info']['gameCreation'],
                    'summonerOnePuuid': match_info['metadata']['participants'][0],
                    'summonerTwoPuuid': match_info['metadata']['participants'][1],
                    'summonerThreePuuid': match_info['metadata']['participants'][2],
                    'summonerFourPuuid': match_info['metadata']['participants'][3],
                    'summonerFivePuuid': match_info['metadata']['participants'][4],
                    'summonerSixPuuid': match_info['metadata']['participants'][5],
                    'summonerSevenPuuid': match_info['metadata']['participants'][6],
                    'summonerEightPuuid': match_info['metadata']['participants'][7],
                    'summonerNinePuuid': match_info['metadata']['participants'][8],
                    'summonerTenPuuid': match_info['metadata']['participants'][9],

                    'summonerOneriotIdGameName': riotIdGameName_list[0],
                    'summonerTworiotIdGameName': riotIdGameName_list[1],
                    'summonerThreeriotIdGameName': riotIdGameName_list[2],
                    'summonerFourriotIdGameName': riotIdGameName_list[3],
                    'summonerFiveriotIdGameName':  riotIdGameName_list[4],
                    'summonerSixriotIdGameName': riotIdGameName_list[5],
                    'summonerSevenriotIdGameName': riotIdGameName_list[6],
                    'summonerEightriotIdGameName': riotIdGameName_list[7],
                    'summonerNineriotIdGameName': riotIdGameName_list[8],
                    'summonerTenriotIdGameName': riotIdGameName_list[9],

                    'summonerOneriotIdTagline': riotIdTagline_list[0],
                    'summonerTworiotIdTagline': riotIdTagline_list[1],
                    'summonerThreeriotIdTagline':riotIdTagline_list[2],
                    'summonerFourriotIdTagline':riotIdTagline_list[3],
                    'summonerFiveriotIdTagline': riotIdTagline_list[4],
                    'summonerSixriotIdTagline': riotIdTagline_list[5],
                    'summonerSevenriotIdTagline': riotIdTagline_list[6],
                    'summonerEightriotIdTagline': riotIdTagline_list[7],
                    'summonerNineriotIdTagline': riotIdTagline_list[8],
                    'summonerTenriotIdTagline': riotIdTagline_list[9],

                    'summonerOneChampionName': match_info['info']['participants'][0]['championName'],
                    'summonerTwoChampionName': match_info['info']['participants'][1]['championName'],
                    'summonerThreeChampionName':match_info['info']['participants'][2]['championName'],
                    'summonerFourChampionName':match_info['info']['participants'][3]['championName'],
                    'summonerFiveChampionName': match_info['info']['participants'][4]['championName'],
                    'summonerSixChampionName': match_info['info']['participants'][5]['championName'],
                    'summonerSevenChampionName': match_info['info']['participants'][6]['championName'],
                    'summonerEightChampionName': match_info['info']['participants'][7]['championName'],
                    'summonerNineChampionName': match_info['info']['participants'][8]['championName'],
                    'summonerTenChampionName': match_info['info']['participants'][9]['championName'],

                    "teamBlueId": match_info['info']['teams'][0]['teamId'],
                    "teamBlueBan": list(match_info['info']['teams'][0]['bans'][i]['championId'] for i in range(5)),
                    "teamBluePick" : teamBluePick,
                    "teamBlueWin": match_info['info']['teams'][0]['win'],
                    "teamBlueGold": goldSum[match_info['info']['teams'][0]['teamId']],
                    "teamBlueBaronKills": match_info['info']['teams'][0]['objectives']['baron']['kills'],
                    "teamBlueChampionKills": match_info['info']['teams'][0]['objectives']['champion']['kills'],
                    "teamBlueDragonKills": match_info['info']['teams'][0]['objectives']['dragon']['kills'],
                    "teamBlueHordeKills": match_info['info']['teams'][0]['objectives']['horde']['kills'],
                    "teamBlueInhibitorKills": match_info['info']['teams'][0]['objectives']['inhibitor']['kills'],
                    "teamBlueRiftheraldKills": match_info['info']['teams'][0]['objectives']['riftHerald']['kills'],
                    "teamBlueTowerKills": match_info['info']['teams'][0]['objectives']['tower']['kills'],
                    "teamRedId": match_info['info']['teams'][1]['teamId'],
                    "teamRedBan": list(match_info['info']['teams'][1]['bans'][i]['championId'] for i in range(5)),
                    "teamRedPick": teamRedPick,
                    "teamRedWin": match_info['info']['teams'][1]['win'],
                    "teamRedGold": goldSum[match_info['info']['teams'][1]['teamId']],
                    "teamRedBaronKills": match_info['info']['teams'][1]['objectives']['baron']['kills'],
                    "teamRedChampionKills": match_info['info']['teams'][1]['objectives']['champion']['kills'],
                    "teamRedDragonKills": match_info['info']['teams'][1]['objectives']['dragon']['kills'],
                    "teamRedHordeKills": match_info['info']['teams'][1]['objectives']['horde']['kills'],
                    "teamRedInhibitorKills": match_info['info']['teams'][1]['objectives']['inhibitor']['kills'],
                    "teamRedRiftheraldKills": match_info['info']['teams'][1]['objectives']['riftHerald']['kills'],
                    "teamRedTowerKills": match_info['info']['teams'][1]['objectives']['tower']['kills'],
                }
                match_result = requests.post(append_match_info_url, json = per_match_info)
        #최근 10경기 요약 
        st.write("함께한 최근 10경기 요약")
        tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(['All', 'vsLevel', 'vsKills', 'vsDeaths', 'vsAssists', 'vsGold', 'vsTDDTC', 'vsTDT', 'vsTH', 'vsTTCCD', 'vsVS'])
        vsscoreDict0 = {}
        vsscoreDict1 = {}
        vsscoreDict2 = {}
        vsscoreDict3 = {}
        vsscoreDict4 = {}
        vsscoreDict5 = {}
        vsscoreDict6 = {}
        vsscoreDict7 = {}
        vsscoreDict8 = {}
        vsscoreDict9 = {}
        vsscoreDict10 = {}
        for match_number in range(len(match_id_list)-11 if len(match_id_list)>=11 else 0, len(match_id_list)):
            match = match_id_list[match_number]
            get_matchinfo_from_db_url = back_url + f'/get-matchinfo-from-db/{match}'
            per_match_info = requests.get(get_matchinfo_from_db_url, params = {'match_id' : match}).json()
            for i in range(len(summoner_list)):
                summoner_info_per_match_url = back_url + f"/get-summonerinfo-from-db/{summoner_puuid_list[i]}/{match}"
                summoner_info_per_match = requests.get(summoner_info_per_match_url).json()
                if summoner_list[i] not in vsscoreDict0:
                    vsscoreDict0[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict1:
                    vsscoreDict1[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict2:
                    vsscoreDict2[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict3:
                    vsscoreDict3[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict4:
                    vsscoreDict4[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict5:
                    vsscoreDict5[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict6:
                    vsscoreDict6[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict7:
                    vsscoreDict7[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict8:
                    vsscoreDict8[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict9:
                    vsscoreDict9[summoner_list[i]] = []
                if summoner_list[i] not in vsscoreDict10:
                    vsscoreDict10[summoner_list[i]] = []    
                info1 = summoner_info_per_match['versuschampionLevel']
                info2 = summoner_info_per_match['versuskills']  
                info3 = summoner_info_per_match['versusdeaths']
                info4 = summoner_info_per_match['versusassists']
                info5 = summoner_info_per_match['versusgoldEarned']
                info6 = summoner_info_per_match['versusTDDTC']
                info7 = summoner_info_per_match['versusTDT']
                info8 = summoner_info_per_match['versusTH']
                info9 = summoner_info_per_match['versusTTCCD']
                info10 = summoner_info_per_match['versusVS']
                info0 = round((info1 * 100 + info2 * 100 + info3 * -100 + info4 + info5 * 150 + info6 / 4 + info7/4 + info8 / 100 + info9 * 5 + info10 * 15)/500, 1)
                vsscoreDict0[summoner_list[i]].append(info0)
                vsscoreDict1[summoner_list[i]].append(info1)
                vsscoreDict2[summoner_list[i]].append(info2)
                vsscoreDict3[summoner_list[i]].append(info3)
                vsscoreDict4[summoner_list[i]].append(info4)
                vsscoreDict5[summoner_list[i]].append(info5)
                vsscoreDict6[summoner_list[i]].append(info6)
                vsscoreDict7[summoner_list[i]].append(info7)
                vsscoreDict8[summoner_list[i]].append(info8)
                vsscoreDict9[summoner_list[i]].append(info9)
                vsscoreDict10[summoner_list[i]].append(info10)
        vsscoreDict0['sequence'] = [i for i in range(1, 1 + len(vsscoreDict0[summoner_list[0]]))]
        vsscoreDict1['sequence'] = [i for i in range(1, 1 + len(vsscoreDict1[summoner_list[0]]))]
        vsscoreDict2['sequence'] = [i for i in range(1, 1 + len(vsscoreDict2[summoner_list[0]]))]
        vsscoreDict3['sequence'] = [i for i in range(1, 1 + len(vsscoreDict3[summoner_list[0]]))]
        vsscoreDict4['sequence'] = [i for i in range(1, 1 + len(vsscoreDict4[summoner_list[0]]))]
        vsscoreDict5['sequence'] = [i for i in range(1, 1 + len(vsscoreDict5[summoner_list[0]]))]
        vsscoreDict6['sequence'] = [i for i in range(1, 1 + len(vsscoreDict6[summoner_list[0]]))]
        vsscoreDict7['sequence'] = [i for i in range(1, 1 + len(vsscoreDict7[summoner_list[0]]))]
        vsscoreDict8['sequence'] = [i for i in range(1, 1 + len(vsscoreDict8[summoner_list[0]]))]
        vsscoreDict9['sequence'] = [i for i in range(1, 1 + len(vsscoreDict9[summoner_list[0]]))]
        vsscoreDict10['sequence'] = [i for i in range(1, 1 + len(vsscoreDict10[summoner_list[0]]))]
        chart_data0 = pd.DataFrame(vsscoreDict0, columns=summoner_list+['sequence'])
        chart_data1 = pd.DataFrame(vsscoreDict1, columns=summoner_list+['sequence'])
        chart_data2 = pd.DataFrame(vsscoreDict2, columns=summoner_list+['sequence'])
        chart_data3 = pd.DataFrame(vsscoreDict3, columns=summoner_list+['sequence'])
        chart_data4 = pd.DataFrame(vsscoreDict4, columns=summoner_list+['sequence'])
        chart_data5 = pd.DataFrame(vsscoreDict5, columns=summoner_list+['sequence'])
        chart_data6 = pd.DataFrame(vsscoreDict6, columns=summoner_list+['sequence'])
        chart_data7 = pd.DataFrame(vsscoreDict7, columns=summoner_list+['sequence'])
        chart_data8 = pd.DataFrame(vsscoreDict8, columns=summoner_list+['sequence'])
        chart_data9 = pd.DataFrame(vsscoreDict9, columns=summoner_list+['sequence'])
        chart_data10 = pd.DataFrame(vsscoreDict10, columns=summoner_list+['sequence'])
        color=["#FF0000", "#0000FF", "#00FF00", "#F0F0F0", "#0F0F0F"]
        tab0.subheader("ALL VS Score")
        tab0.line_chart(chart_data0, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab1.subheader('동일 라인 상대와의 LEVEL 차이')
        tab1.line_chart(chart_data1, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab2.subheader('동일 라인 상대와의 KILL 차이')
        tab2.line_chart(chart_data2, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab3.subheader('동일 라인 상대와의 DEATH 차이')
        tab3.line_chart(chart_data3, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab4.subheader('동일 라인 상대와의 ASSIST 횟수 차이')
        tab4.line_chart(chart_data4, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab5.subheader('동일 라인 상대와의 번 GOLD 차이')
        tab5.line_chart(chart_data5, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab6.subheader('동일 라인 상대와의 가한 피해랑 차이')
        tab6.line_chart(chart_data6, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab7.subheader('동일 라인 상대와의 받은 피해량 차이')
        tab7.line_chart(chart_data7, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab8.subheader('동일 라인 상대와의 총 HEAL 양의 차이')
        tab8.line_chart(chart_data8, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab9.subheader('동일 라인 상대와의 CC기술을 사용한 시간의 차이')
        tab9.line_chart(chart_data9, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        tab10.subheader('동일 라인 상대와의 VISION SCORE 차이')
        tab10.line_chart(chart_data10, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
            
        #경기 마다의 요약 부분       
        for match_number in range(len(match_id_list)-1, -1, -1):
            #경기마다의 정보를 위해 API로 특정 경기의 정보를 받아오고, 그 경기의 참여자 정보도 List형태로 가져옴 
            match = match_id_list[match_number]
            get_matchinfo_from_db_url = back_url + f'/get-matchinfo-from-db/{match}'
            per_match_info = requests.get(get_matchinfo_from_db_url, params = {'match_id' : match}).json()
            summoner_list_per_match = []
            #참여자들의 특정 경기 정보를 DB에서 가져옴 
            for j in range(len(summoner_list)):
                get_summoner_from_db_url = back_url + f'/get-summonerinfo-from-db/{summoner_puuid_list[j]}/{match}'
                summoner_list_per_match.append(requests.get(get_summoner_from_db_url, params = {'puuid': summoner_puuid_list[j],'match_id' : match}).json())
            with st.container(border = True):
                #경기 전체에 대한 요약을 나타내는 부분
                duration_seconds = int(per_match_info['gameDuration'])%60 #경기 진행 시간 
                date = datetime.fromtimestamp(int(per_match_info['gameCreation'])/1000)# 경기를 시작한 시각
                st.write(f"Game Date: {date.date()} / Game Time: {per_match_info['gameDuration']//60}:{duration_seconds:02}") 
                #팀 별 경기 요약 부분(team Blue)
                with st.container(border = True):
                    with st.container():
                        if per_match_info['teamBlueWin'] == 0: #승패 데이터 출력 
                            st.write('<p style="text-align: center; font-size: 2;"><strong>Blue팀 패배 / Red팀 승리</strong></p>', unsafe_allow_html=True)
                        else:
                            st.write('<p style="text-align: center; font-size: 2;"><strong>Blue팀 승리 / Red팀 패배</strong></p>', unsafe_allow_html=True)
                    with st.container(border = True):
                            st.write('<p style="text-align: center; font-size: 2;color:blue;"><strong>Blue Team Data</strong></p>', unsafe_allow_html=True)
                            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                            with col1:#해당 팀의 벌어들인 Gold 데이터 부분
                                with st.container(): 
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Gold", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueGold']}", unsafe_allow_html=True)
                            with col2:#해당 팀이 Baron이라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Baron", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueBaronKills']}", unsafe_allow_html=True)
                            with col3:#해당 팀이 상대 팀을 상대로 kill을 얼마나 했는지 나타내는 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Kills", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueChampionKills']}", unsafe_allow_html=True)
                            with col4:#해당 팀이 Dragon이라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Dragon", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueDragonKills']}", unsafe_allow_html=True)
                            with col5:#해당 팀이 Horde라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Horde", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueHordeKills']}", unsafe_allow_html=True)
                            with col6:#해당 팀이 Inhibitor라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Inhibitor", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueInhibitorKills']}", unsafe_allow_html=True)
                            with col7:#해당 팀이 Herald라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Herald", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueRiftheraldKills']}", unsafe_allow_html=True)
                            with col8:#해당 팀이 상대 팀의 Tower라는 경기 내 특정 요소를 제거한 횟수를 나타낸 부분 
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Tower", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamBlueTowerKills']}", unsafe_allow_html=True)
                    #red team 요약
                    with st.container():
                        with st.container(border = True):
                            st.write('<p style="text-align: center; font-size: 2;color:red;"><strong>Red Team Data</strong></p>', unsafe_allow_html=True)
                            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                            with col1:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Gold", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedGold']}", unsafe_allow_html=True)
                            with col2:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Baron", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedBaronKills']}", unsafe_allow_html=True)
                            with col3:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Kills", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedChampionKills']}", unsafe_allow_html=True)
                            with col4:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Dragon", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedDragonKills']}", unsafe_allow_html=True)
                            with col5:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Horde", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedHordeKills']}", unsafe_allow_html=True)
                            with col6:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Inhibitor", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedInhibitorKills']}", unsafe_allow_html=True)
                            with col7:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Herald", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedRiftheraldKills']}", unsafe_allow_html=True)
                            with col8:
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>Tower", unsafe_allow_html=True)
                                with st.container():
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_match_info['teamRedTowerKills']}", unsafe_allow_html=True)
                    #여기는 챔피언픽(사진), 소환사 이름, 소환사 태그, 벤픽(사진)
                    with st.container():
                        with st.container():
                            col1, col2, col3 = st.columns([9, 3, 9])
                            with col1:
                                st.write('<p style="text-align: center; font-size: 2;color : blue;"><strong>BLUE</strong></p>', unsafe_allow_html=True)
                            with col2:
                                st.write('<p style="text-align: center; font-size: 2;"><strong>Ban & Pick</strong></p>', unsafe_allow_html=True)
                            with col3:
                                st.write('<p style="text-align: center; font-size: 2;color: red;"><strong>RED</strong></p>', unsafe_allow_html=True)
                        for k in range(5):
                            with st.container():
                                col1, col2, col3, col4, col5, col6 = st.columns([0.4, 2, 0.4, 0.4, 2, 0.4])
                                #픽 이미지
                                with col1:
                                    per_summoner_champion_per_match = per_match_info[f'summoner{number_list[k]}ChampionName']
                                    per_summoner_pick_key = per_match_info['teamBluePick'][k]
                                    per_summoner_pick = str(9999999)
                                    for champion_key in champion_data['data']:
                                        if champion_data['data'][champion_key]['key'] ==  str(per_summoner_pick_key):
                                            per_summoner_pick = champion_data['data'][champion_key]['id']
                                            break
                                    pick_imange_url = str(0)
                                    pick_image_url = image_url + f"{champion_data['data'][per_summoner_pick]['image']['full']}"
                                    pick_image = requests.get(pick_image_url, stream=True).content
                                    pil_image = Image.open(io.BytesIO(pick_image))
                                    st.image(pil_image, use_column_width = True)
                                #소환사 이름
                                with col2:
                                    per_summoner_name = per_match_info[f'summoner{number_list[k]}riotIdGameName']
                                    per_summoner_tagline = per_match_info[f'summoner{number_list[k]}riotIdTagline']
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_summoner_name}#{per_summoner_tagline}</p>", unsafe_allow_html=True)
                                # 밴 이미지
                                with col3:
                                    per_summoner_ban_key = per_match_info['teamBlueBan'][k]
                                    per_summoner_ban = str(9999999)
                                    for champion_key in champion_data['data']:
                                        if champion_data['data'][champion_key]['key'] ==  str(per_summoner_ban_key):
                                            per_summoner_ban = champion_data['data'][champion_key]['id']
                                            break
                                    ban_imange_url = str(0)
                                    if per_summoner_ban == '9999999':
                                        ban_image_url = 'https://ddragon.leagueoflegends.com/cdn/5.5.1/img/ui/champion.png'
                                    else:
                                        ban_image_url = image_url + f"{champion_data['data'][per_summoner_ban]['image']['full']}"
                                    ban_image = requests.get(ban_image_url, stream=True).content
                                    pil_image = Image.open(io.BytesIO(ban_image))
                                    grayscale_image = pil_image.convert("L")
                                    st.image(grayscale_image, use_column_width = True)

                                with col4:
                                    per_summoner_ban_key = per_match_info['teamRedBan'][k]
                                    per_summoner_ban = str(9999999)
                                    for champion_key in champion_data['data']:
                                        if champion_data['data'][champion_key]['key'] ==  str(per_summoner_ban_key):
                                            per_summoner_ban = champion_data['data'][champion_key]['id']
                                            break
                                    ban_imange_url = str(0)
                                    if per_summoner_ban == '9999999':
                                        ban_image_url = 'https://ddragon.leagueoflegends.com/cdn/5.5.1/img/ui/champion.png'
                                    else:
                                        ban_image_url = image_url + f"{champion_data['data'][per_summoner_ban]['image']['full']}"
                                    ban_image = requests.get(ban_image_url, stream=True).content
                                    pil_image = Image.open(io.BytesIO(ban_image))
                                    grayscale_image = pil_image.convert("L")
                                    st.image(grayscale_image, use_column_width = True)

                                with col5:
                                    per_summoner_name = per_match_info[f'summoner{number_list[k+5]}riotIdGameName']
                                    per_summoner_tagline = per_match_info[f'summoner{number_list[k+5]}riotIdTagline']
                                    st.write(f"<p style='text-align: center; font-size: 2;'>{per_summoner_name}#{per_summoner_tagline}</p>", unsafe_allow_html=True)
                                    
                                with col6:
                                    per_summoner_champion_per_match = per_match_info[f'summoner{number_list[k+5]}ChampionName']
                                    per_summoner_pick_key = per_match_info['teamRedPick'][k]
                                    per_summoner_pick = str(9999999)
                                    for champion_key in champion_data['data']:
                                        if champion_data['data'][champion_key]['key'] ==  str(per_summoner_pick_key):
                                            per_summoner_pick = champion_data['data'][champion_key]['id']
                                            break
                                    pick_imange_url = str(0)
                                    pick_image_url = image_url + f"{champion_data['data'][per_summoner_pick]['image']['full']}"
                                    pick_image = requests.get(pick_image_url, stream=True).content
                                    pil_image = Image.open(io.BytesIO(pick_image))
                                    st.image(pil_image, use_column_width = True)

                            
                        
                # 각 플레이어마다의 요약 정보
                for i in range(len(summoner_list)):
                    info = 0
                    with st.container(border = True):
                        st.write(f"<p style='text-align: center; font-size: 2;'><strong>{summoner_list[i]}'s VS Score</strong></p>", unsafe_allow_html=True) 
                        summoner_info_per_match_url = back_url + f"/get-summonerinfo-from-db/{summoner_puuid_list[i]}/{match}"
                        summoner_info_per_match = requests.get(summoner_info_per_match_url).json()
                        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.25, 0.25, 0.25, 0.25, 0.25, 0.3, 0.3, 0.3, 0.25, 0.3])
                        info1 = summoner_info_per_match['versuschampionLevel']
                        info2 = summoner_info_per_match['versuskills']  
                        info3 = summoner_info_per_match['versusdeaths']
                        info4 = summoner_info_per_match['versusassists']
                        info5 = summoner_info_per_match['versusgoldEarned']
                        info6 = summoner_info_per_match['versusTDDTC']
                        info7 = summoner_info_per_match['versusTDT']
                        info8 = summoner_info_per_match['versusTH']
                        info9 = summoner_info_per_match['versusTTCCD']
                        info10 = summoner_info_per_match['versusVS']
                        with col1:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Level</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info1}</p>", unsafe_allow_html=True)
                        with col2:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Kill</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info2}</p>", unsafe_allow_html=True)
                        with col3:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Death</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info3}</p>", unsafe_allow_html=True)
                        with col4:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Assist</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info4}</p>", unsafe_allow_html=True)
                        with col5:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Gold</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info5}</p>", unsafe_allow_html=True)
                        with col6:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Dealt</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info6}</p>", unsafe_allow_html=True)
                        with col7:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Taken</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info7}</p>", unsafe_allow_html=True)
                        with col8:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Heal</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info8}</p>", unsafe_allow_html=True)
                        with col9:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>CC</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info9}</p>", unsafe_allow_html=True)
                        with col10:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>Vision</p>", unsafe_allow_html=True)
                            st.write(f"<p style='text-align: center; font-size: 2;'>{info10}</p>", unsafe_allow_html=True)
                        info = round((info1 * 100 + info2 * 100 + info3 * -100 + info4 + info5 * 150 + info6 / 4 + info7/4 + info8 / 100 + info9 * 5 + info10 * 15)/500, 1)
                            
                    
                    with st.container():
                        if info<0:
                            st.write(f"<div style='text-align: center; font-size: 20px; color: black;'><strong>VS SCORE : </strong><span style='color: red;'>{info}</span></div>", unsafe_allow_html=True)
                        else:
                            st.write(f"<div style='text-align: center; font-size: 20px; color: black;'><strong>VS SCORE : </strong><span style='color: green;'>{info}</span></div>", unsafe_allow_html=True)
                        
                        if info<-400:
                            if summoner_info_per_match['win']:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신은 버스 승객입니다.</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신 때문에 패배했네요!</p>", unsafe_allow_html=True)
                        elif info < -50:
                            if summoner_info_per_match['win']:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신은 버스 승객입니다.</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신의 플레이가 아쉬웠어요..</p>", unsafe_allow_html=True)
                        elif info>400:
                            if summoner_info_per_match['win']:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신의 캐뤼이이이이이!</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>팀운이 아쉽습니다.</p>", unsafe_allow_html=True)
                        elif info>150:
                            if summoner_info_per_match['win']:
                                    st.write(f"<p style='text-align: center; font-size: 2;'><strong>준수한 활약을 하셨네요.</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>어느 정도 잘 했는데 아쉽습니다.</p>", unsafe_allow_html=True)
                        elif info>=50:
                            if summoner_info_per_match['win']:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>1인분은 하셨습니다.</p>", unsafe_allow_html=True)
                            else:
                                st.write(f"<p style='text-align: center; font-size: 2;'><strong>당신의 직접적인 영향은 아닌 것 같아요.</p>", unsafe_allow_html=True)
                        else:
                            st.write(f"<p style='text-align: center; font-size: 2;'><strong>상대와 우열을 가리기 힘드네요.</p>", unsafe_allow_html=True)    

        # st.write("함께한 최근 10경기 요약")
        # #원하는 데이터에 대한 그래프를 얻을 수 있는 tab 생성
        # tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(['All', 'vsLevel', 'vsKills', 'vsDeaths', 'vsAssists', 'vsGold', 'vsTDDTC', 
        #                                                                              'vsTDT', 'vsTH', 'vsTTCCD', 'vsVS'])
        # #예시 VS score 변화 그래프 분석 
        # vsscoreDict0 = {} #검색한 사용자들의 변화 데이터를 저장하는 dictionary 선언
        # #최근 10경기 데이터를 찾아 반복문을 통해 vsscoreDict에 저장(최근 진행한 100경기 중 같이 한 경기가 10경기가 되지 않는다면 해당 경기들만을 가지고 그래프 그림)
        # for match_number in range(len(match_id_list)-11 if len(match_id_list)>=11 else 0, len(match_id_list)):
        #     match = match_id_list[match_number] #각 경기의 고유 id를 가지고 옴 
        #     #API를 통해 데이터베이스에서 경기 정보를 가지고 옴 
        #     get_matchinfo_from_db_url = back_url + f'/get-matchinfo-from-db/{match}'
        #     per_match_info = requests.get(get_matchinfo_from_db_url, params = {'match_id' : match}).json()

        #     #검색한 사용자들(summoner)마다의 특정 경기에서의 데이터들을 DB에서 가져오고 그 값들로 VS score를 계산 
        #     for i in range(len(summoner_list)):
        #         #특정 경기에서의 특정 사용자의 경기 데이터를 가지고 옴 
        #         summoner_info_per_match_url = back_url + f"/get-summonerinfo-from-db/{summoner_puuid_list[i]}/{match}"
        #         summoner_info_per_match = requests.get(summoner_info_per_match_url).json()
        #         if summoner_list[i] not in vsscoreDict0:
        #             vsscoreDict0[summoner_list[i]] = []
        #         info1 = summoner_info_per_match['versuschampionLevel']
        #         info2 = summoner_info_per_match['versuskills']  
        #         info3 = summoner_info_per_match['versusdeaths']
        #         info4 = summoner_info_per_match['versusassists']
        #         info5 = summoner_info_per_match['versusgoldEarned']
        #         info6 = summoner_info_per_match['versusTDDTC']
        #         info7 = summoner_info_per_match['versusTDT']
        #         info8 = summoner_info_per_match['versusTH']
        #         info9 = summoner_info_per_match['versusTTCCD']
        #         info10 = summoner_info_per_match['versusVS']

        #         #레벨, 도움 횟수 등의 정보들을 통해 VS score 계산 
        #         info0 = round((info1 * 100 + info2 * 100 + info3 * -100 + info4 + info5 * 150 + info6 / 4 + info7/4 + info8 / 100 + info9 * 5 + info10 * 15)/500, 1)
        # #저장된 데이터들에 index 부여하여 DataFrame 자료형으로 변환 
        # vsscoreDict0['sequence'] = [i for i in range(1, 1 + len(vsscoreDict0[summoner_list[0]]))]
        # chart_data0 = pd.DataFrame(vsscoreDict0, columns=summoner_list+['sequence'])
        # #그래프에서 사용자들을 구분하기 위한 색 선언 
        # color=["#FF0000", "#0000FF", "#00FF00", "#F0F0F0", "#0F0F0F"]
        # #해당 tab에서 VS score에 대한 그래프를 확인할 수 있도록 코드 작성 
        # tab0.subheader("ALL VS Score")
        # tab0.line_chart(chart_data0, x = 'sequence', y = summoner_list, color=color[0:len(summoner_list)])
        
            
                        