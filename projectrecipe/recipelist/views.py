from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from django.http import HttpResponse
from fractions import Fraction
from django.shortcuts import render, redirect
import os
import time
from urllib.parse import quote
from pretty_html_table import build_table
import pandas as pd
import re




ingredients=[]

def index(request):
    return render(request, 'recipelist/index.html')

def get_ingredients(request):
    if request.method == 'POST':
        url = request.POST['url']
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        stars_html = soup.find(id='mntl-recipe-review-bar__rating_2-0')
        ingredients_html = soup.find(class_='mntl-structured-ingredients__list')
        directions_html= soup.find(class_='comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup')
        ingredients = []
        directions = []
        stars = ''
        if stars_html:
            stars = stars_html.text
        if ingredients_html:
            for li in ingredients_html.find_all('li'):
                ingredients.append(li.text.strip())
        if directions_html:
            for li in directions_html.find_all('li'):
                directions.append(li.text.replace('.', '--').strip())

        context = {
            'url': url,
            'stars': stars,
            'ingredients': ingredients,
            'directions': directions,
        }

        return render(request, 'recipelist/ingredients.html', context)

    else:
        return render(request, 'recipelist/index.html')




def search(request):
    query = request.GET.get('q', '')
    url = f"https://www.google.com/search?q={query} site:allrecipes.com"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    search_results = soup.find_all('a')

    recipe_url = None
    for link in search_results:
        link_url = link.get('href')
        if link_url.startswith('/url?q=https://www.allrecipes.com/recipe/') and 'search' not in link_url:
            recipe_url = link_url.split('&')[0][7:]
            break

    if not recipe_url:
        return render(request, 'search.html', {'error_message': 'No recipe found.'})

    recipe_page = requests.get(recipe_url)
    recipe_soup = BeautifulSoup(recipe_page.content, 'html.parser')

    recipe_title = soup.find("title").text
    title, source = recipe_title.split(":")


    recipe_details = recipe_soup.find('div', {'class': 'comp recipe-details mntl-recipe-details'})
    details_items = recipe_details.find_all('div', {'class': 'mntl-recipe-details__item'})

    for item in details_items:
        label = item.find('div', {'class': 'mntl-recipe-details__label'}).text.strip()
        if label == 'Servings:':
            servings = item.find('div', {'class': 'mntl-recipe-details__value'}).text.strip()
            break
    else:
        servings = None


    stars = recipe_soup.find(id='mntl-recipe-review-bar__rating_2-0')
    if stars:
        stars_text = f'{stars.text} -- Ingredients:  '
    else:
        stars_text = 'Could not find stars information.'

    ingredients = []
    ingredients_html = recipe_soup.find(class_='mntl-structured-ingredients__list')
    for li in ingredients_html.find_all('li'):
        ingredients.append(li.text.strip())

    directions = []
    directions_html = recipe_soup.find(class_='comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup')
    for li in directions_html.find_all('li'):
        directions.append(li.text.replace('.', '--').strip())

    # Extract the image URL using regular expressions
    image_pattern = re.compile(r'"(https://www\.allrecipes\.com/[^"]+\.jpg)"')
    image_match = re.search(image_pattern, recipe_page.text)
    image_url = image_match.group(1) if image_match else None

    context = {
        'recipe_url': recipe_url,
        'stars_text': stars_text,
        'servings': servings,
        'ingredients': ingredients,
        'directions': directions,
        'recipe_title': recipe_title,
        'title':title,
        'source':source,
        'image_url': image_url,
    }
    return render(request, 'recipelist/search.html', context)





def adjusted_search(request):
    servings = request.GET.get('servings', '')
    recipe_url = request.GET.get('recipe_url', '')
    if not servings or not recipe_url:
        return redirect('search')

    try:
        servings = int(servings)
        if servings < 1 or servings > 10:
            raise ValueError
    except ValueError:
        return redirect('search')

    recipe_page = requests.get(recipe_url)
    recipe_soup = BeautifulSoup(recipe_page.content, 'html.parser')

    recipe_title = recipe_soup.find("title").text
    if ':' in recipe_title:
        title, source = recipe_title.split(":")
    else:
        title = recipe_title
        source = "Unknown"

    recipe_details = recipe_soup.find('div', {'class': 'comp recipe-details mntl-recipe-details'})
    details_items = recipe_details.find_all('div', {'class': 'mntl-recipe-details__item'})

    for item in details_items:
        label = item.find('div', {'class': 'mntl-recipe-details__label'}).text.strip()
        if label == 'Servings:':
            old_servings = int(item.find('div', {'class': 'mntl-recipe-details__value'}).text.strip())
            break
    else:
        old_servings = None

    stars = recipe_soup.find(id='mntl-recipe-review-bar__rating_2-0')
    if stars:
        stars_text = f'{stars.text} -- Ingredients:  '
    else:
        stars_text = 'Could not find stars information.'

    ingredients = []
    ingredients_html = recipe_soup.find(class_='mntl-structured-ingredients__list')
    for li in ingredients_html.find_all('li'):
        ingredient_text = li.text.strip()
        if '(' in ingredient_text and ')' in ingredient_text:
            # Remove parentheses and their contents, e.g. "(10 oz.)"
            start_index = ingredient_text.find('(')
            end_index = ingredient_text.find(')') + 1
            ingredient_text = ingredient_text[:start_index] + ingredient_text[end_index:]
        ingredient_parts = ingredient_text.split()
        try:
            amount = float(ingredient_parts[0])
            unit = ingredient_parts[1]
            name = ' '.join(ingredient_parts[2:])
            adjusted_amount = round(amount * servings / old_servings, 2)
            ingredient_text = f'{adjusted_amount} {unit} {name}'
        except (ValueError, IndexError):
            pass  # Leave ingredient text unchanged if parsing fails
        ingredients.append(ingredient_text)

    directions = []
    directions_html = recipe_soup.find(class_='comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup')
    for li in directions_html.find_all('li'):
        directions.append(li.text.replace('.', '--').strip())

    context = {
        'recipe_url': recipe_url,
        'stars_text': stars_text,
        'servings': servings,
        'ingredients': ingredients,
        'directions': directions,
        'recipe_title': recipe_title,
        'title': title,
        'source': source,
    }
    return render(request, 'recipelist/adjusted_search.html', context)


from django.contrib.sessions.backends.db import SessionStore




def search_store(request):
    query = request.GET.get('q', '')
    url = f"https://www.google.com/search?q={query} site:allrecipes.com"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    search_results = soup.find_all('a')

    recipe_url = None
    for link in search_results:
        link_url = link.get('href')
        if link_url.startswith('/url?q=https://www.allrecipes.com/recipe/') and 'search' not in link_url:
            recipe_url = link_url.split('&')[0][7:]
            break

    if not recipe_url:
        return render(request, 'search.html', {'error_message': 'No recipe found.'})

    recipe_page = requests.get(recipe_url)
    recipe_soup = BeautifulSoup(recipe_page.content, 'html.parser')

    recipe_title = soup.find("title").text
    title, source = recipe_title.split(":")


    recipe_details = recipe_soup.find('div', {'class': 'comp recipe-details mntl-recipe-details'})
    details_items = recipe_details.find_all('div', {'class': 'mntl-recipe-details__item'})

    for item in details_items:
        label = item.find('div', {'class': 'mntl-recipe-details__label'}).text.strip()
        if label == 'Servings:':
            servings = item.find('div', {'class': 'mntl-recipe-details__value'}).text.strip()
            break
    else:
        servings = None


    stars = recipe_soup.find(id='mntl-recipe-review-bar__rating_2-0')
    if stars:
        stars_text = f'{stars.text} -- Ingredients:  '
    else:
        stars_text = 'Could not find stars information.'

    ingredients = []
    ingredients_html = recipe_soup.find(class_='mntl-structured-ingredients__list')
    for li in ingredients_html.find_all('li'):
        ingredients.append(li.text.strip())

    directions = []
    directions_html = recipe_soup.find(class_='comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup')
    for li in directions_html.find_all('li'):
        directions.append(li.text.replace('.', '--').strip())

    context = {
        'recipe_url': recipe_url,
        'stars_text': stars_text,
        'servings': servings,
        'ingredients': ingredients,
        'directions': directions,
        'recipe_title': recipe_title,
        'title':title,
        'source':source,
    }
    return render(request, 'recipelist/search.html', context)

def grocery_list(request):
    if request.method == 'POST':
        selected_ingredients = request.POST.getlist('ingredient')
        request.session['selected_ingredients'] = selected_ingredients
        recipe_name = request.POST.get('recipe_name', '')
        request.session['recipe_name'] = recipe_name

    return render(request, 'recipelist/grocery_list.html', {'ingredients':selected_ingredients})



def api_test(request):
    selected_ingredients = request.session.get('selected_ingredients')
    print("Selected Ingredients:", selected_ingredients)  # Debug print

    if not selected_ingredients:
        print("No selected ingredients found in the session.")  # Debug print
        return render(request, 'recipelist/api_test.html', {'table_html': '', 'ingredients': selected_ingredients})

    url = "https://nutrition-by-api-ninjas.p.rapidapi.com/v1/nutrition"
    headers = {
        "X-RapidAPI-Host": "nutrition-by-api-ninjas.p.rapidapi.com",
        "X-RapidAPI-Key": "ffda10e22cmshcb6236d6bc8f365p1b8b5djsn88764eb5fd75",
    }

    nutrition_data = []

    for ingredient in selected_ingredients:
        querystring = {"query": ingredient}
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            nutrition_data.append(df)  # Append data to the list
        else:
            print(f"Error: {response.status_code}, {response.text}")

    if nutrition_data:
        # If there's data, build the table for all ingredients
        combined_df = pd.concat(nutrition_data)  # Combine all DataFrames
        table_html = build_table(combined_df, 'blue_light')

        return render(request, 'recipelist/api_test.html', {'table_html': table_html, 'ingredients': selected_ingredients})
    else:
        print("No data available or there was an error fetching data.")

    # If there's no data or an error occurred, pass an empty string as the HTML table to the template
    return render(request, 'recipelist/api_test.html', {'table_html': '', 'ingredients': selected_ingredients})

from django.core.mail import send_mail
from django.conf import settings
from .forms import SendTextForm

def send_text(request):
    if request.method == 'POST':
        form = SendTextForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            carrier = form.cleaned_data['carrier']

            if carrier == 'sprint':
                # If the carrier is Sprint, use a different email format
                email_address = f'{phone_number}@pm.sprint.com'
            else:
                # For other carriers, use the default format
                email_address = f'{phone_number}@txt.{carrier}.net'


            # Send the email (You need to implement this part)
            # For example, using Django's EmailMessage
            from django.core.mail import EmailMessage

            subject = 'Selected Ingredients'
            message = '\n'.join(request.session.get('selected_ingredients', []))
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email_address]

            email = EmailMessage(subject, message, from_email, recipient_list)
            email.send()

            return render(request, 'recipelist/success_page.html')  # Redirect to a success page
    else:
        form = SendTextForm()

    return render(request, 'recipelist/send_text.html', {'form': form})



def success_page(request):
    return render(request, 'recipelist/success_page.html')



































































































































