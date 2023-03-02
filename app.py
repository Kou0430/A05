from flask import Flask, render_template, redirect, request, session
from cs50 import SQL
import sqlite3

app = Flask(__name__)
# ※セッションを使いたいのでapp.secret_keyが必要？
app.secret_key = 'abcde'
db = SQL("sqlite:///recipe.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/food-recipe", methods=['GET', 'POST'])
def food_recipe():
    if request.method == "POST":
        # 入力がなければこのページにとどまる
        if not request.form.get('food1'):
            return  render_template("food-recipe.html")
        foods = [""] * 5

        foods[0] = request.form.get('food1')

        if request.form.get('food2'):
            foods[1] = request.form.get('food2')

        if request.form.get('food3'):
            foods[2] = request.form.get('food3')

        if request.form.get('food4'):
            foods[3] = request.form.get('food4')

        if request.form.get('food5'):
            foods[4] = request.form.get('food5')

        # データベースに接続
        conn = sqlite3.connect('recipe.db')
        c = conn.cursor()

        # レシピを検索
        c.execute("SELECT recipe_title, recipe_url, food_image_url, id FROM recipe WHERE recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ?", ('%'+foods[0]+'%', '%'+foods[1]+'%', '%'+foods[2]+'%', '%'+foods[3]+'%', '%'+foods[4]+'%'))

        results = c.fetchall()

        # 辞書型に変換してhtmlに渡せるようにする

        # DBに重複があったのでユニークな辞書型リストにする
        uniquelist = []

        checklist = []
        for i in range(len(results)):
            if results[i][0] not in checklist:
                dic = {}
                dic['recipe_title'] = results[i][0]
                dic['recipe_url'] = results[i][1]
                dic['food_image_url'] = results[i][2]
                dic['id'] = results[i][3]
                checklist.append(results[i][0])
                uniquelist.append(dic)

        # 検索結果をセッションで保持
        idlist = []
        for i in range(len(uniquelist)):
            idlist.append(uniquelist[i]['id'])
        session['recipes'] = idlist

        # 10件以上なら10件まで表示
        if len(uniquelist) > 10:
            displaylist = []
            for i in range(10):
                displaylist.append(uniquelist[i])
        # ページ数
            pages = int(len(uniquelist)/10)+1

            return render_template("recipe-search.html", recipes=displaylist, pages=range(pages+1), num=len(uniquelist))
        else:
            return render_template("recipe-search.html", recipes=uniquelist, pages=range(1+1), num=len(uniquelist))

    else:
        return render_template("food-recipe.html")

@app.route("/recipe-food")
def recipe_food():
    return render_template("recipe-food.html")

@app.route("/recipe-search", methods=['GET', 'POST'])
def pagenation_recipe_search():
    if request.method == 'POST':
        # ページ数を取得
        pagenum = int(request.form.get("pagenation"))
        # 検索したレシピのidを取得
        recipeidlist = session['recipes']

        conn = sqlite3.connect('recipe.db')
        c = conn.cursor()
        # idからレシピの情報を検索するが、指定するidの数を可変にするため、formatで?を検索件数の数だけ置換している
        c.execute("SELECT recipe_title, recipe_url, food_image_url, id FROM recipe WHERE id IN ({})".format(','.join('?'*len(recipeidlist))), tuple(recipeidlist))

        recipelist = c.fetchall()
        # 辞書型にしてhtmlに渡せるようにする
        for i in range(len(recipeidlist)):
            dic = {}
            dic['recipe_title'] = recipelist[i][0]
            dic['recipe_url'] = recipelist[i][1]
            dic['food_image_url'] = recipelist[i][2]
            dic['id'] = recipelist[i][3]
            recipelist[i] = dic
        displaylist = []
        # そのページに表示する10件を取り出す
        try:
            for i in range((pagenum-1)*10, pagenum*10):
                displaylist.append(recipelist[i])
        # 10件に満たなければ操作を終える
        except IndexError:
            pass

        return render_template("recipe-search.html", recipes=displaylist, pages=range(int(len(recipelist)/10)+1))

