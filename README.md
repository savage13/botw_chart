Breath of the Wild Speedrun Charts
----------------------------------

Single page chart displaying the time progression
of speedruns for the Legend of Zelda: Breath of the Wild.

Data is obtained from speedrun.com/botw/ and the associated API.

Setup
-----

   # Create the "site"
   npm install
   npm run build

   # Get the data
   #   - curl needs to be installed and in the path
   ./get_data.py -a -p -f all

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

