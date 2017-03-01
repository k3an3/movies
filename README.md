# movies
Picks movies

A quick-and-dirty python3 solution to pick a random movie using Slack's slash commands or the Flask web frontend.
Live version at https://movies.105ww.xyz. I am not responsible for the content on this page as it is from external sources.

## Installation
Set up a slash command on Slack.

```
git clone https://github.com/keaneokelley/movies.git
cd movies
cp example-config_local.py config_local.py
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
# If using systemd
cp movies.service /etc/systemd/system # make sure to configure ExecStart/WorkingDirectory paths!
sudo systemctl start movies
# or, to run on port 5000
python3 main.py
```

You'll also need to give chores its own user and edit sudoers (`visudo`) if you want chores to be able to update itself and restart the service using systemctl:
```chores ALL=NOPASSWD: /bin/systemctl restart movies```

## Slash Commands
`/movies` in Slack, followed by:
```
choose [category] - Select a random movie in the given category. To pick from all categories, no extra argument is necessary.
watched [movie] - Mark a movie as watched. This will prevent it from being selected again.
add [movie] - Add a movie to the list that you'd like to watch in the future.
list [movies|genres] - List all of the movies or genres that exist within the database.
```
