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
    if request.method == "GET":
        # 検索キーワードがない場合、入力画面にリダイレクト
        if not request.args.get("q",""):
            return redirect("/recipe-food")

        # 検索キーワードを取得
        searchTitle = request.args.get("q","")

        # DB設定
        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        # ページ数（入力がない場合は1）
        page = 1
        offset = 0
        if request.args.get("p",""):
            page = int(request.args.get("p",""))
            offset = (int(page) - 1) * 10

        # レシピ数を取得し、ページングの総数を計算
        recipeAmount = cur.execute("SELECT COUNT(DISTINCT recipe_title) FROM recipe WHERE recipe_title LIKE ? ORDER BY id ASC", ('%'+searchTitle+'%',))
        recipeAmount = int(recipeAmount.fetchall()[0][0])
        pageAmount = math.ceil(recipeAmount / 10)

        # ページング
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

        # 検索結果を入れる配列
        result = []

        # レシピ総数が0以外なら
        if recipeAmount:
            # レシピ検索
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

        # コネクションを閉じる
        conn.close()

        return render_template("food-search.html", result=result, searchTitle=searchTitle, page=page, pageList=pageList, recipeAmount=recipeAmount, pageAmount=pageAmount)

@app.route("/foodlist", methods=["GET"])
def foodlist():
    if request.method == "GET":
        # レシピIDが指定されていない場合、検索画面にリダイレクト
        if not request.args.get("id",""):
            return redirect("/recipe-food")

        # レシピIDを取得
        recipeId = request.args.get("id","")

        # DB設定
        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        # 該当レシピを検索
        recipeDetailByRecipeId = cur.execute("SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE id = ?", (recipeId,))

        # 結果を入れる変数
        result = {}

        recipeDetailFetchall = recipeDetailByRecipeId.fetchall()
        if len(recipeDetail):
            recipeDetail = recipeDetailFetchall[0]

            # 結果を加工・resultに詰める
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
        else:
            # レシピIDが存在しなかった場合、検索画面にリダイレクト
            return redirect("/recipe-food")

        # コネクションを閉じる
        conn.close()

        return render_template("foodlist.html", result=result)
