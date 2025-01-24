## Hello! Welcome to Priveedly

Priveedly is a personal content and feed reader with the ability to build your own small personalized machine learning models. Priveedly helps you follow, read, save what you like on your own server.

Currently supported content:

- Any valid RSS feed
- Subreddits
- [HackerNews](https://news.ycombinator.com/) hottest
- [Lobste.rs](https://lobste.rs/) hottest

No longer supported but might work:

- Twitter/X API

The project is built using the [Django web framework](https://www.djangoproject.com/), [scikit-learn](https://scikit-learn.org/stable/) and with very minimal Javascript and Python-based feed scraping. It is currently only useful for you if you know Python and can navigate setting up your own server.

> A short video [introduction to Priveedly is on YouTube](https://youtu.be/_aHZlSUO8Qs)

If this is too advanced for you, stay tuned! I plan to find some one-click install setups for non-dev/tech folks. 🙂

### Why run your own content and feed-reader?

- 🎯 **Autonomy**: Decide what types of content you want to read and update yourself without an algorithm.
- 🔐 **Privacy**: It's a private service, for you and by you. Unless you give someone your login, they won't read your feed.
- 💸 **No ads**: Because why do you want ads in the middle of your reading?
- 🤓 **Self-study**: Because training ML models for yourself and by yourself can be a fun way to safely do data science and ML without contributing your data to a large-scale content platform.

You can read more [about my experience and motivation on my blog](https://blog.kjamistan.com/priveedly-your-private-and-personal-content-reader-and-recommender.html).

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

This repository doesn't yet have an easy one-click launch, but I am hoping someone might contribute that!

For those who already know Python, the basic setup is as follows:

1. Clone the repository:
```bash
 git clone https://github.com/kjam/priveedly.git
```

2. Create a virtual or Conda environment.
```bash
 conda create -n priveedly
 ```

3. Install dependencies:
```bash
 conda install pip
 pip install -r requirements.txt
 ```

4. Create database that can be used with Django, like postgresql (or your favorite database here).

5. Add environment file with necessary variables, see [example environment file](example_env). This needs to then be saved as '.env' in the main directory.

6. Migrate the database.
```bash
python manage.py makemigrations
python manage.py migrate
 ```

7. Create a super user.
```bash
python manage.py createsuperuser
 ```

8. Run the server and navigate to /admin to log in.
 ```bash
 python manage.py runserver
  ```

The project is currently only tested on Python 3.9, but appears to work for other versions. Due to the dependencies, you might need to hold back your Python version if you plan on using things like Jupyter, scikit-learn, etc to train your models.

## Usage

### Local use

First, get everything installed above and working. Then, you can enter a few feeds and subreddits you might like to read. To do so, add the feeds directly in the admin website (navigate there after running the runserver command).

Then, you can test whether the parsing is working properly by opening a new terminal in your virtual environment and then running the following command.

```bash
python manage.py parse_all
 ```

This command parses your saved feeds, Subreddits along with HackerNews and Lobste.rs top stories. If you'd like to change the parsing, please update the /feeds/commands/parse_all.py file.

You can then navigate to the homepage when logged in (http://127.0.0.1:8000) and see the parsed feeds. The general reading flow is as follows:

- ⏳ **Progress Bar**: On the top you have a bar telling you how far you are along in your reading backlog. It's very minimal and if you want to change it or redesign it, feel free!

- 📚 **Articles**: Each page loads an oldest-first of all of your different feeds, reddits and other stories from HN and lobsters. If you click on the titles of any article, it will navigate to that article (use CNTRL+click if you want to open in a new tab).

- ✅️ **Read Later**: If you see something you want to read later, click read later and it will be saved for later access. To see your read-later, navigate to http://127.0.0.1:8000/read-later

- 📊 To train your **own recommendation model**, you'll need to save things to read-later, and then mark the content you like as interesting. If you want to use a different workflow, you could also change the main view to expose the interesting button on the main page.

- 🗂️ **Recommended**: Once you have your own recommendation model running, you can visit http://127.0.0.1:8000/recommended to skip to the articles you might like the most.

I wouldn't recommend running locally if you want to use it regularly, because it has the ability to parse and run in the background if you get it setup on a server. (see below)

For the first few thousand entries, I wouldn't bother trying to train or use the machine learning parts because it won't be enough data for a useful model. Once you have many thousands of posts, it's worth using the machine learning example. If you are new to building language classification models, I recommend starting by watching [my video](https://youtu.be/AMy3K3NbrLw) and then trying it for yourself by running Jupyter in the notebooks folder and following along.

To get Reddit working, you'll need to [sign up to get an API key](https://praw.readthedocs.io/en/stable/getting_started/configuration.html#configuration) and then store that in your environment file. To see how to do that, please see the [example environment file](example_env). That should then be saved as '.env' in the main directory.

### Personal server use

Ideally, you have access to a server and can get Priveedly set up on that server. If you are familiar with [Ansible](https://docs.ansible.com/ansible/latest/index.html), you can see several reference scripts for your use in the deployment folder but they probably require updates or modifications based on your operating system and cloud provider.

If you are willing to contribute a Dockerfile to ease deployment for those unfamiliar with Ansible, I would greatly appreciate any contributions.

Important to note that when using a server, you'll want:

- Enough storage to store all of your favorite articles and run the parser
- Eventually enough RAM to run ML classification tasks
- Good connectivity/throughput for parsing

I recommend running the parse_all command every 2-3 hours if you plan on using the app relatively frequently.

Once you have enough data to train your own model, you'll want to do that locally and then deploy it to the server.

### Training your own model

If machine learning is new to you, you can get started by watching [my YouTube video](https://youtu.be/AMy3K3NbrLw) and then trying it for yourself by running Jupyter in the notebooks folder and following along.

> Note: When/if you modify the data preparation steps, you must also modify the rate_all.py script in the feeds/management/commands folder. The data going into the model on the server must match how the model was trained.

Once your model is trained, I recommend running the rate_all about once a day or every 6 hours if you have an especially busy feedreader.

I'm happy to also host more Notebook and training contributions if you find a different model type works well for you, if you have another notebook that works better for a different set of languages or a more production-ready setup. You can also post your own notebook and explanations on your own site/repo for others to learn from!

### Some additional notes

1. So long tweets: Twitter changed their API and moved to paid only access after I had already been using this reader for a year or so. 😩 Therefore, I am not sure if the /tweets section still works anymore or not. If you are an active X user and want to test it out and let me know, I'd appreciate the feedback!

2. One-click deploy: I'd be really happy if someone wants to figure out an easy way for people to one-click deploy this. If you offer a service like this, please let me know and I'll see if I can get the repository in a shape to get it working!

3. Monkeypatching with Django: I originally started monkeypatching some of the sites parsing to add tests, only to find that django testing and monkeypatching are a bit of a pain when used together. If you have experience making these play nice, I'd love some help.

4. Supporting other languages and classifiers with beginner-friendly instructions: Because I'd like this to be useful for people of all ML-levels and also folks who like reading non-English texts, it'd be awesome to have more Jupyter contributions and accompanying posts/videos to help folks test out different types of one-person-use recommenders. Contributions are very welcome!

## Contributions

I heartily welcome contributions that would benefit others. First and foremost, please use the project yourself before making significant contributions.

I also suggest looking through the Issues for open asks from myself and other users.

In general, please follow the following workflow:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes. Please include tests if providing significant new functionality.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

## License

The project is shared under the [GNU Public License](LICENSE).
