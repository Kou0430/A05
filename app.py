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

        searchTitle = request.args.get("q","")

        page = 1
        offset = 0

        if request.args.get("p",""):
            page = int(request.args.get("p",""))
            offset = (int(page) - 1) * 10

        recipeAmount = cur.execute("SELECT COUNT(DISTINCT recipe_title) FROM recipe WHERE recipe_title LIKE ? ORDER BY id ASC", ('%'+searchTitle+'%',))
        recipeAmount = int(recipeAmount.fetchall()[0][0])

        result = []

        pageAmount = math.ceil(recipeAmount / 10)

        # ページネーション
        pageList = []
        pageList.append(1)
        pagecount = 0
        if pageAmount <= page + 3:
            pagecount = pageAmount - 1
        elif page == 1:
            pagecount = page + 4
        elif page == 2:
            pagecount = page + 3
        else:
            pagecount = page + 2
        for i in range(4):
            if pagecount <= 1:
                break
            pageList.insert(1, pagecount)
            pagecount -= 1
        if pageAmount > 0:
            pageList.append(pageAmount)
        # END ページネーション

        recipeLists = cur.execute("SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE id IN (SELECT MIN(id) AS id FROM recipe WHERE recipe_title LIKE ? GROUP BY recipe_title ORDER BY id ASC) ORDER BY id ASC LIMIT 10 OFFSET ?", ('%'+searchTitle+'%', offset))

        for recipeList in recipeLists.fetchall():
            recipeId = int(recipeList[0])
            recipeTitle = recipeList[1]
            recipeUrl = recipeList[2]
            foodImageUrl = recipeList[3]
            recipeMaterial = recipeList[4]

            recipeMaterial = recipeMaterial.replace('[', '')
            recipeMaterial = recipeMaterial.replace(']', '')
            recipeMaterial = recipeMaterial.replace('\'', '')
            recipeMaterial = recipeMaterial.split(",")

            dict = {}
            dict["recipeId"] = recipeId
            dict["recipeTitle"] = recipeTitle
            dict["recipeUrl"] = recipeUrl
            dict["foodImageUrl"] = foodImageUrl
            dict["recipeMaterial"] = recipeMaterial
            result.append(dict)

        # セッションを閉じる
        conn.close()

        return render_template("food-search.html", result=result, searchTitle=searchTitle, page=page, pageList=pageList, recipeAmount=recipeAmount, pageAmount=pageAmount)

@app.route("/foodlist", methods=["GET"])
def foodlist():
    # メイン関数
    if request.method == "GET":
        if not request.args.get("id",""):
            return render_template("foodlist.html")

        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        recipeId = request.args.get("id","")

        recipeDetailByRecipeId = cur.execute("SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE id = ?", (recipeId,))

        recipeDetail = recipeDetailByRecipeId.fetchall()[0]

        recipeId = int(recipeDetail[0])
        recipeTitle = recipeDetail[1]
        recipeUrl = recipeDetail[2]
        foodImageUrl = recipeDetail[3]
        recipeMaterial = recipeDetail[4]

        recipeMaterial = recipeMaterial.replace('[', '')
        recipeMaterial = recipeMaterial.replace(']', '')
        recipeMaterial = recipeMaterial.replace('\'', '')
        recipeMaterial = recipeMaterial.split(",")

        dict = {}
        dict["recipeId"] = recipeId
        dict["recipeTitle"] = recipeTitle
        dict["recipeUrl"] = recipeUrl
        dict["foodImageUrl"] = foodImageUrl
        dict["recipeMaterial"] = recipeMaterial
        result = dict

        return render_template("foodlist.html", result=result)
