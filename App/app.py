
from flask import Flask

from flask import make_response,redirect,request, url_for,abort,Response, render_template,flash,session
from werkzeug.urls import url_parse
import altair as alt
import pandas as pd
import numpy as np
from vega_datasets import data
from flask import jsonify
from App.forms import selectJob
import datetime
from altair.expr import datum



ENV = "local"

# My own MongoDB Cluster
# app.config['MONGO_DBNAME'] = 'SportsBet'
# app.config['MONGO_URI'] = 'mongodb+srv://admin:ads2sportsbet@ads-2.l7gr9.mongodb.net/SportsBet?retryWrites=true&w=majority'

app = Flask(__name__)


app.config['SECRET_KEY'] = 'dcqJQC6nAXEyz3k5'
app.config['SESSION_PROTECTION'] = 'strong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


#from App.models import


@app.route("/")
def home():
    form = selectJob(request.form)

    return render_template("index.html", form=form)


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error/505.html'), 500

@app.route("/data/<job>")
def chart(job):
    if job == "dress": job = "Dressmaker / Seamstress"
    source = data.jobs.url

    chart = alt.Chart(source,width=950,height=400).mark_line().encode(
        alt.X('year:O',title="Year"),
        alt.Y('perc:Q', axis=alt.Axis(format='%'),title="Percentage"),
        color=alt.Color('sex:N',title="Gender"),
    ).properties(
        title='Percent of population working as '+ job
    ).transform_filter(
        datum.job == job
    )

    return chart.to_json()


@app.route("/data/best_team/<year>/<top>")
def best(year,top):
    year = int(year)
    if top =="top":
        return bestTeamPlot(year,True)
    return bestTeamPlot(year,False)


def bestTeamPlot(year,top):

    bigDf = pd.read_csv("App/Data/CumulativeSeasons.csv")

    dfSeason = bigDf[bigDf['season'] == str(year+2000)+"/"+str((year+1)+2000)]

    if top:
        df = dfSeason.groupby(['result', 'team_long_name']).size()['won'].sort_values(ascending=False)[:5]
    else:
        df = dfSeason.groupby(['result', 'team_long_name']).size()['won'].sort_values()[:5]
    teamList = df.index.tolist()

    num_players = 11
    df_won = []
    df_lost = []
    df_draw = []
    for i in df.index:
        won = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][2]) / num_players)
        lost = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][1]) / num_players)
        draw = int((dfSeason.groupby(['team_long_name', "result"]).size()[i][0]) / num_players)

        df_won.append(won)
        df_lost.append(lost)
        df_draw.append(draw)
    best = pd.DataFrame({'Team': teamList, 'Wins': df_won, 'Losts': df_lost, 'Draw': df_draw})

    best.to_csv("best.csv",index=None)

    chart = alt.Chart(pd.melt(best, id_vars=['Team'], var_name='Result', value_name='Total'),height=400,width=165).mark_bar().encode(
        alt.X('Result:N', axis=alt.Axis(title="",labels=False)),
        alt.Y('Total:Q', axis=alt.Axis(title='Total', grid=False)),
        alt.Tooltip(["Total:Q"]),
        color=alt.Color('Result:N'),
        column=alt.Column('Team:O',sort=alt.EncodingSortField("Total", op='max',order='descending'),title="")
    ).configure_view(
        stroke='transparent'
    ).interactive()

    return chart.to_json()



if __name__ == '__main__':
    app.run()
