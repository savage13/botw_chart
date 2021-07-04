Breath of the Wild Speedrun Charts
----------------------------------

Single page "serverless" chart displaying the time progression of speedruns for the Legend of Zelda: Breath of the Wild.
All files and data for a particular category are fetched on page load.

Data is obtained from [Speedrun BotW](https://speedrun.com/botw/) and the associated [API](https://github.com/speedruncomorg/api).

Setup
-----

    # Create the "site"
    npm install
    npm run build

    # Get the data
    #   curl needs to be installed and in the path
    #     -a  - Get all data (creates ${cat}.json and ${cat}2.json
    #     -p  - Get/Update player data (creates player.json and player2.json)
    #     -f  - Filters/Removes data unnecessary to the page construction
    #     all - Get all the categories
    ./get_data.py -a -p -f all
    
    # Run Development site locally
    npm run dev 

Categories
----------

Currently available categories are:
  - Any%
  - AD (All Dungeons)
  - AMQ (All Main Quests)
  - AS (All Shrines)
  - 100%

Options within each category are dependent on what was decided by the
moderators at speedrun.com. We have attempted to follow the categories
and optons with the most runs.

Dependencies
------------
- [speedrun.com](https://www.speedrun.com/) for the data
- [Chart.js](https://chartjs.org)
- [Svelte](https://svelte.dev)
- [Luxon](https://moment.github.io/luxon/)

License
-------
This is licensed under the MIT License

