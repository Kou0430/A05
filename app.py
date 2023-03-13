from flask import Flask, render_template, redirect, request, session, g
import sqlite3
import math
import os
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE="recipe.db"

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager= LoginManager()
login_manager.init_app(app)

# ※セッションを使いたいのでapp.secret_keyが必要？
app.secret_key = 'abcde'

class User(UserMixin):
    def __init__(self, userid):
        self.id = userid

## ログイン
@login_manager.user_loader
def load_user(userid):
    return User(userid)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    session.clear()
    return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    error_message = ''
    username = ''

    if request.method == 'POST':
        # 入力を受け取る
        username = request.form.get('username')
        password = request.form.get('password')

        # ログインのチェック
        user_data = get_db().execute(
            "SELECT password FROM user WHERE username=?",[username,]
        ).fetchone()
        if username is not None:
            if check_password_hash(user_data[0],password):
                user_id = get_db().execute("SELECT id FROM user WHERE username = ?", [username,]).fetchone()
                session["user_id"] = user_id[0]
                user = User(username)
                login_user(user)
                return redirect("/")

        error_message = '入力されたIDもしくはパスワードが誤っています'

    return render_template("login.html", username=username, error_message=error_message)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 入力を受け取る
        username = request.form.get('username')

        if not username:
            return redirect("/register")

        password = request.form.get('password')

        if not password:
            return redirect("/register")

        confirmation = request.form.get('confirmation')

        if password != confirmation:
            return redirect("/register")

        # パスワードをハッシュ化
        pass_hash = generate_password_hash(password, method = 'sha256')


        db = get_db()
        # 入力されたユーザーネームが使われてないか確認
        usercheck = get_db().execute("SELECT username from user WHERE username=?",[username,]).fetchall()

        # 新規登録をする
        if not usercheck:
            db.execute(
                "INSERT INTO user (username,password) values(?,?)",
                [username,pass_hash]
            )
            db.commit()
            return redirect('/login')
        else:
            error_message = '入力されたユーザー名はすでに登録されています'

    return render_template("register.html")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


# @app.route("/bookmarks")
# @login_required
# def bookmarks():
#     recipe_ids = get_db().execute("SELECT recipe_id FROM bookmark WHERE user_id = ?", [session["user_id"], ]).fetchall()

#     bookmarks = []

#     for recipe_id in recipe_ids:
#         bookmarks.append(get_db().execute("SELECT * FROM bookmark WHERE id = ?", [recipe_id["recipe_id"], ]).fetchone())

#     rows = get_db().execute("SELECT recipe_id FROM like WHERE user_id=?", [session['user_id'], ]).fetchall()
#     bookmark_RecipeIds = []

#     for row in rows:
#         if not row['review_id'] in like_ReviewIds:
#             bool_ReviewIds.append(row['review_id']
#     return render_template("bookmarks.html")


@app.route("/food-recipe", methods=['GET', 'POST'])
@login_required
def food_recipe():
    if request.method == "POST":
        # 入力がなければこのページにとどまる
        if not request.form.get('food1'):
            return render_template("food-recipe.html")
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
        c.execute("SELECT recipe_title, recipe_url, food_image_url, id FROM recipe WHERE recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ? AND recipe_material LIKE ?",
                  ('%'+foods[0]+'%', '%'+foods[1]+'%', '%'+foods[2]+'%', '%'+foods[3]+'%', '%'+foods[4]+'%'))

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


@app.route("/recipe-search", methods=['GET', 'POST'])
@login_required
def recipe_search():
    if request.method == 'POST':
        # ページ数を取得
        pagenum = int(request.form.get("pagenation"))
        # 検索したレシピのidを取得
        recipeidlist = session['recipes']

        conn = sqlite3.connect('recipe.db')
        c = conn.cursor()
        # idからレシピの情報を検索するが、指定するidの数を可変にするため、formatで?を検索件数の数だけ置換している
        c.execute("SELECT recipe_title, recipe_url, food_image_url, id FROM recipe WHERE id IN ({})".format(
            ','.join('?'*len(recipeidlist))), tuple(recipeidlist))

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

        rows = get_db().execute("SELECT recipe_id FROM bookmark WHERE user_id=?", [session['user_id'], ])
        bookmark_recipeIds = []

        for row in rows:
            if not row['recipe_id'] in bookmark_recipeIds:
                bookmark_recipeIds.append(row['recipe_id'])
        print(bookmark_recipeIds)

        return render_template("recipe-search.html", recipes=displaylist, pages=range(int(len(recipelist)/10)+1), bookmark_recipeIds = bookmark_recipeIds)


@app.route("/recipe-food", methods=['GET', 'POST'])
@login_required
def recipe_food():
    if request.method == "POST":
        # 送信された料理名を格納している
        cooking = request.form.get('cooking')

        if not cooking:
            return render_template("recipe-food.html")

        recipes = get_db().execute("SELECT * FROM recipe WHERE recipe_title LIKE ? GROUP BY recipe_title LIMIT 20",
                                   ('%'+cooking+'%',)).fetchall()

        return render_template("food-search.html", recipes=recipes)
    return render_template("recipe-food.html")


@app.route("/food-search", methods=["GET"])
@login_required
def food_search():
    if request.method == "GET":
        # 検索キーワードがない場合、入力画面にリダイレクト
        if not request.args.get("q", ""):
            return redirect("/recipe-food")

        # 検索キーワードを取得
        searchTitle = request.args.get("q", "")

        # DB設定
        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        # ページ数（入力がない場合は1）
        page = 1
        offset = 0
        if request.args.get("p", ""):
            page = int(request.args.get("p", ""))
            offset = (int(page) - 1) * 10

        # レシピ数を取得し、ページングの総数を計算
        recipeAmount = cur.execute(
            "SELECT COUNT(DISTINCT recipe_title) FROM recipe WHERE recipe_title LIKE ? ORDER BY id ASC", ('%'+searchTitle+'%',))
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
            recipeLists = cur.execute(
                "SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE id IN (SELECT MIN(id) AS id FROM recipe WHERE recipe_title LIKE ? GROUP BY recipe_title ORDER BY id ASC) ORDER BY id ASC LIMIT 10 OFFSET ?", ('%'+searchTitle+'%', offset))

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
@login_required
def foodlist():
    if request.method == "GET":
        # レシピIDが指定されていない場合、検索画面にリダイレクト
        if not request.args.get("id", ""):
            return redirect("/recipe-food")

        # レシピIDを取得
        recipeId = request.args.get("id", "")

        # DB設定
        dbname = 'recipe.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        # 該当レシピを検索
        recipeDetailByRecipeId = cur.execute(
            "SELECT id, recipe_title, recipe_url, food_image_url, recipe_material FROM recipe WHERE id = ?", (recipeId,))

        # 結果を入れる変数
        result = {}

        recipeDetailFetchall = recipeDetailByRecipeId.fetchall()
        if len(recipeDetailFetchall):
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

@app.route("/<id>/recipe-search/bookmark", methods={"GET", "POST"})
@login_required
def recipeSearch_bookmark(id):
    get_db().execute("INSERT INTO bookmark (user_id, recipe_id) VALUES(?,?)",[session["user_id"], id,])

    get_db().commit()

    return redirect("/bookmarks")

@app.route("/<id>/recipe-search/bookmark-release", methods={"GET", "POST"})
@login_required
def recipeSearch_bookmarkRelease(id):
    get_db().execute("DELETE FROM bookmark WHERE user_id=? AND recipe_id=?",[session["user_id"], id,])

    get_db().commit()

    return redirect("/bookmarks")

# database
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
