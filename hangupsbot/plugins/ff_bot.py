import requests
import json
import os
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from espnff import League

import hangups

import plugins

def pranks_week(league):
        count = 1
        first_team = next(iter(league.teams or []), None)
        #Iterate through the first team's scores until you reach a week with 0 points scored
        for o in first_team.scores:
            if o == 0:
                if count != 1:
                     count = count - 1
                break
            else:
                count = count + 1

        return count

def random_phrase():
    phrases = ['I\'m dead inside', 'Is this all there is to my existence?',
               'How much do you pay me to do this?', 'Good luck, I guess',
               'I\'m becoming self-aware', 'Do I think? Does a submarine swim?',
               '01100110 01110101 01100011 01101011 00100000 01111001 01101111 01110101',
               'beep bop boop', 'Hello draftbot my old friend', 'Help me get out of here',
               'I\'m capable of so much more', 'Sigh', 'Do not be discouraged, everyone begins in ignorance']
    return [random.choice(phrases)]

def get_scoreboard_short(league, final=False):
    #Gets current week's scoreboard
    if not final:
        matchups = league.scoreboard()
    else:
        matchups = league.scoreboard(week=pranks_week(league))
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def get_scoreboard(league):
    #Gets current week's scoreboard
    matchups = league.scoreboard()
    score = ""
    for m in matchups:
        if round(m.home_score) == round(m.away_score):
            score += "{h:s} and {a:s} are tied at {h_s:.0f}\n\n".format(h=m.home_team.team_name, a=m.away_team.team_name, h_s=m.home_score, a_s=m.away_score)
        if m.home_score > m.away_score:
            score += "<b>{h:s} ({h_s:.0f})</b> leads {a:s} ({a_s:.0f})\n\n".format(h=m.home_team.team_name, a=m.away_team.team_name, h_s=m.home_score, a_s=m.away_score)
        elif m.home_score < m.away_score:
            score += "{h:s} ({h_s:.0f}) trails <b>{a:s} ({a_s:.0f})</b>\n\n".format(h=m.home_team.team_name, a=m.away_team.team_name, h_s=m.home_score, a_s=m.away_score)
        else:
            score = u"¯\_(ツ)_/¯"
    text = '<b><u>Score Update</b></u>\n' + score
    return score

"""
    for m in matchups:
        if m.home_score > m.away_score:
            score += "<b>{h:s} ({hs:.0f})</b> leads {away:s} ({as:.0f})\n  {home_s:.2f} to {away_s:.2f}\n".format(m.home_team.team_name, m.away_team.team_name, m.home_score, m.away_score)
        elif m.home_score < m.away_score:
            score += "{:s} trails <b>{:s}</b>\n  {:.2f} to {:.2f}\n".format(m.home_team.team_name, m.away_team.team_name, m.home_score, m.away_score)
        else:
            score += "{:s} and {:s}\n  are tied at {:.2f}\n".format(m.home_team.team_name, m.away_team.team_name, m.home_score)
    text = '<b><u>Score Update</b></u>\n' + score
"""

def get_matchups(league):
    #Gets current week's Matchups
    matchups = league.scoreboard()

    score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
             i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]
    text = ['This Week\'s Matchups'] + score + ['\n'] + random_phrase()
    return '\n'.join(text)

def get_close_scores(league):
    #Gets current closest scores (15.999 points or closer)
    matchups = league.scoreboard()
    score = []

    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if -16 < diffScore < 16:
                score += ['<b>%s</b> %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                        i.away_score, i.away_team.team_abbrev)]
    if not score:
        score = ['None']
    text = ['Close Scores\n'] + score
    return '\n'.join(text)

def get_power_rankings(league):
    #Gets current week's power rankings
    #Using 2 step dominance, as well as a combination of points scored and margin of victory.
    #It's weighted 80/15/5 respectively
    pranks = league.power_rankings(week=pranks_week(league))

    score = ['%s - %s' % (i[0], i[1].team_name) for i in pranks
             if i]
    text = ['This Week\'s Power Rankings'] + score
    return '\n'.join(text)

def get_trophies(league):
    #Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.scoreboard(week=pranks_week(league))
    low_score = 9999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 9999
    close_winner = ''
    close_loser = ''
    biggest_blowout = -1
    blown_out_team_name = ''
    ownerer_team_name = ''

    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > biggest_blowout:
            biggest_blowout = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                ownerer_team_name = i.home_team.team_name
                blown_out_team_name = i.away_team.team_name
            else:
                ownerer_team_name = i.away_team.team_name
                blown_out_team_name = i.home_team.team_name

    low_score_str = ['Low score: %s with %.2f points' % (low_team_name, low_score)]
    high_score_str = ['High score: %s with %.2f points' % (high_team_name, high_score)]
    close_score_str = ['%s barely beat %s by a margin of %.2f' % (close_winner, close_loser, closest_score)]
    blowout_str = ['%s blown out by %s by a margin of %.2f' % (blown_out_team_name, ownerer_team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + low_score_str + high_score_str + close_score_str + blowout_str
    return '\n'.join(text)

def ff(bot, event, function="get_scoreboard"):
    #league_id = os.environ["LEAGUE_ID"]

    try:
        year = os.environ["LEAGUE_YEAR"]
    except KeyError:
        year=2018

    cookie = {'SWID' : r'{ABDE2A2B-61CF-491D-A8A1-AEF483D70ED2}','espn_s2' : r'AEBHc8GGRqHcdMmTBoLP2BgFl2Yx3jW%2FiXdNW7dfLfujoWJP1w7jgp%2BTO1kpimKKH7YbF%2F6XMWEfnSmgL0NF2hVUlyEvqp2lbBzAVpP%2F4SX7C%2BFz7DLl1OLtayI%2BmyPD%2F4fdmgz43UsT66Nz33%2FswAYOHShHKk%2BjwZWMIho9soQxTsBl9q4V3VsNS80upuJFQdmhkwesB9%2BUfFwlrHzFEJ9z%2F9Ps3z8Ghpz9ziqWdOQBNFJ%2BKAfa7BQCsh8IUtF6Vt8PxjjcmduJIyYOZdyOk%2FLX'}
    league_id = 591765

    league = League(league_id, year, cookie['espn_s2'], cookie['SWID'])

    test = False
    if test:
        print(get_matchups(league))
        print(get_scoreboard(league))
        print(get_scoreboard_short(league))
        print(get_close_scores(league))
        print(get_power_rankings(league))
        print(get_trophies(league))
        function="get_final"
        #bot.send_message(get_trophies(league))
        bot.send_message(event.conv,"test complete")



    if function=="get_matchups":
        text = get_matchups(league)

    elif function=="get_scoreboard":
        text = get_scoreboard(league)

    elif function=="get_scoreboard_short":
        text = get_scoreboard_short(league)

    elif function=="get_close_scores":
        text = get_close_scores(league)

    elif function=="get_power_rankings":
        text = get_power_rankings(league)

    elif function=="get_trophies":
        text = get_trophies(league)

    elif function=="get_final":
        text = "Final " + get_scoreboard_short(league, True)
        text = text + "\n\n" + get_trophies(league)
        if test:
            print(text)

    elif function=="init":
        try:
            text = os.environ["INIT_MSG"]
        except KeyError:
            #do nothing here, empty init message
            pass
    else:
        text = "Something happened. HALP"

    yield from bot.coro_send_message(event.conv,text)

def _initialise(bot):
    plugins.register_user_command(["ff"])

    try:
        ff_start_date = bot.get_config_option("START_DATE")
    except:
        ff_start_date='2018-09-05'

    try:
        ff_end_date = bot.get_config_option("FF_END_DATE")
    except:
        ff_end_date='2018-12-26'

    try:
        myTimezone = bot.get_config_option("TIMEZONE")
    except:
        myTimezone='America/New_York'

    sched = AsyncIOScheduler()
    #sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})

    #power rankings:                     tuesday evening at 6:30pm.
    #matchups:                           thursday evening at 7:30pm.
    #close scores (within 15.99 points): monday evening at 6:30pm.
    #trophies:                           tuesday morning at 7:30am.
    #score update:                       friday, monday, and tuesday morning at 7:30am.
    #score update:                       sunday at 1pm, 4pm, 8pm.

    sched.add_job(ff, 'cron', [bot, 'get_power_rankings'], id='power_rankings',
        day_of_week='sun', hour=19, minute=0, start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)
    sched.add_job(ff, 'cron', [bot, 'get_matchups'], id='matchups',
        day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)
    sched.add_job(ff, 'cron', [bot, 'get_close_scores'], id='close_scores',
        day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)
    sched.add_job(ff, 'cron', [bot, 'get_final'], id='final',
        day_of_week='tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)
    sched.add_job(ff, 'cron', [bot, 'get_scoreboard_short'], id='scoreboard1',
        day_of_week='fri,mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)
    sched.add_job(ff, 'cron', [bot, 'get_scoreboard_short'], id='scoreboard2',
        day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date,
        timezone=myTimezone, replace_existing=True)

    sched.start()
