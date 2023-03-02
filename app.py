from flask import Flask, render_template, redirect, request, g, session
import sqlite3

# データベースの名前を格納
DATABASE="recipe.db"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/food-recipe", methods=['GET', 'POST'])
def food_recipe():
    if request.method == "POST":

        # 入力された材料を変数に格納
        material1 = request.form.get('material1')

        if not material1:
            return redirect('food-recipe')

        material2 = request.form.get('material2')

        # material2~5は入力が空白だった場合""
        if not material2:
            material2 = ""

        material3 = request.form.get('material3')

        if not material3:
            material3 = ""

        material4 = request.form.get('material4')

        if not material4:
            material4 = ""


        material5 = request.form.get('material5')

        if not material5:
            material5 = ""


        # 材料からレシピ情報を取得
        recipes = get_db().execute("SELECT * FROM recipe WHERE recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? GROUP BY recipe_title LIMIT 20", ('%'+material1+'%', '%'+material2+'%', '%'+material3+'%', '%'+material4+'%', '%'+material5+'%', )).fetchall()

        return render_template("recipe-search.html", recipes=recipes)
    return render_template("food-recipe.html")

@app.route("/recipe-food", methods=['GET', 'POST'])
def recipe_food():
    if request.method == "POST":
        # 送信された料理名を格納している
        cooking = request.form.get('cooking')

        if not cooking:
            return render_template("recipe-food.html")

        recipes = get_db().execute("SELECT * FROM recipe WHERE recipe_title LIKE ? GROUP BY recipe_title LIMIT 20", ('%'+cooking+'%',)).fetchall()

        return render_template("food-search.html", recipes=recipes)
    return render_template("recipe-food.html")

@app.route("/foodlist", methods=['GET', 'POST'])
def foodlist():
    if request.method == "GET":
        return render_template("foodlist.html")

#database
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db