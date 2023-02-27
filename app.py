from flask import Flask, render_template, redirect, request

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
