from flask import Flask, render_template, redirect, request
import math
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/food-recipe")
def food_recipe():
    return render_template("food-recipe.html")

@app.route("/recipe-food")
def recipe_food():
    return render_template("recipe-food.html")

@app.route("/food-search", methods=["GET"])
def food_search():
    # メイン関数
    if request.method == "GET":
        if not request.args.get("q",""):
            return render_template("food-search.html")

        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        recipeTitle = request.args.get("q","")

        page = 1
        offset = 0

        if request.args.get("p",""):
            page = request.args.get("p","")
            offset = (int(page) - 1) * 10

        # Debug
        app.logger.debug(recipeTitle)


        recipeAmount = cur.execute("SELECT COUNT(id) FROM recipe WHERE recipe_title LIKE ? ORDER BY id ASC", ('%'+recipeTitle+'%',))

        result = []

        pageAmount = math.ceil(int(recipeAmount.fetchall()[0][0]) / 10)
        # Debug
        app.logger.debug(pageAmount)

        recipeLists = cur.execute("SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE recipe_title LIKE ? ORDER BY id ASC LIMIT 10 OFFSET ?", ('%'+recipeTitle+'%', offset))
        # Debug
        app.logger.debug(recipeLists)

        for recipeList in recipeLists.fetchall():
            # Debug
            # app.logger.debug(int(recipeList["id"]))
            # app.logger.debug(recipeList[0])

            recipeId = int(recipeList[0])
            recipe_title = recipeList[1]
            recipe_url = recipeList[2]
            food_image_url = recipeList[3]
            recipe_material = recipeList[4]
            dict = {}
            dict["id"] = recipeId
            dict["recipe_title"] = recipe_title
            dict["recipe_url"] = recipe_url
            dict["food_image_url"] = food_image_url
            dict["recipe_material"] = recipe_material
            result.append(dict)

        # Debug
        # app.logger.debug(result)

        # セッションを閉じる
        conn.close()

        return render_template("food-search.html", result=result, recipeTitle=recipeTitle, pageAmount=pageAmount)
