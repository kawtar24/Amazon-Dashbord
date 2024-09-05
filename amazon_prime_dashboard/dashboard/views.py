from django.shortcuts import render
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import plotly.io as pio

def index(request):
    context = {}
    
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)
        else:
            context['error'] = "Unsupported file format"
            return render(request, 'index.html', context)
        
        # Calculations for statistics
        total_titles = data['title'].nunique()
        total_ratings = data['rating'].nunique()
        total_genres = data['listed_in'].nunique()
        total_directors = data['director'].nunique()
        
        # Process genres
        data['primary_genre'] = data['listed_in'].apply(lambda x: x.split(',')[0] + '...' if ',' in x else x)
        genre_counts = data['primary_genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        filtered_genre_counts = genre_counts[genre_counts['Count'] > 30]
        
        # Create bar chart
        fig = px.bar(filtered_genre_counts, x='Genre', y='Count', text='Count')
        graph_html = pio.to_html(fig, full_html=False)
        
        # Process country data and create choropleth map
        country_counts = data['country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        fig_map = px.choropleth(country_counts, locations='Country', locationmode='country names', color='Count')
        map_html = pio.to_html(fig_map, full_html=False)
        
        # Create 3D pie chart for Movies and TV Shows
        type_counts = data['type'].value_counts()
        type_percentages = (type_counts / type_counts.sum()) * 100
        fig = go.Figure(data=[go.Pie(labels=type_percentages.index, values=type_percentages.values)])
        fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1] * len(type_percentages), marker=dict(line=dict(color='#000000', width=2)))
        pie = pio.to_html(fig, full_html=False)
        
        # Line chart for TV Shows and Movies by release year
        if 'release_year' in data.columns and 'type' in data.columns:
            tv_shows = data[data['type'] == 'TV Show']
            movies = data[data['type'] == 'Movie']
            tv_show_counts = tv_shows['release_year'].value_counts().sort_index()
            movie_counts = movies['release_year'].value_counts().sort_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tv_show_counts.index, y=tv_show_counts.values, mode='lines', name='TV Shows'))
            fig.add_trace(go.Scatter(x=movie_counts.index, y=movie_counts.values, mode='lines', name='Movies'))
            fig.update_layout(xaxis_title="Release Year", yaxis_title="Total Shows", legend_title="Type")
            line = pio.to_html(fig, full_html=False)
            
        else:
            context['error'] = "'release_year' or 'type' column not found"

        # Horizontal histogram for ratings
        if 'rating' in data.columns:
            rating_counts = data['rating'].value_counts()
            fig = px.bar(x=rating_counts.values, y=rating_counts.index, orientation='h', labels={'x': 'Total Shows', 'y': 'Rating'})
            histogram = pio.to_html(fig, full_html=False)
            context['histo'] = histogram
        else:
            context['error'] = "'rating' column not found"
        
        # Add data to context
        context.update({
            'total_titles': total_titles,
            'total_ratings': total_ratings,
            'total_genres': total_genres,
            'total_directors': total_directors,
            'graph': graph_html,
            'map': map_html,
            'pie': pie,
            'line': line,
            'histo': histogram,
            'all_genres': data[['primary_genre', 'listed_in']].drop_duplicates().set_index('primary_genre').to_dict()['listed_in']
        })
    
    return render(request, 'index.html', context)
