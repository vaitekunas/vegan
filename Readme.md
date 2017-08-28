# Vegan

`Vegan` is a simplistic spam filter. Add your email accounts, learn a spam classifier
and let vegan veganize your inbox.

## Training a model

```python

from vegan import Vegan
from vegan.learners import NaiveBayes

# Initiate Vegan
vegan = Vegan()

# Add one or more email accounts to fetch data from
# (NB: Will be prompted to enter passwords)
vegan.add_account("myemail", "my.imapserver.com", 993, "me@myemail.com", spam_folder = "junk", ssl=True)
vegan.add_account("otheremail", "another.imapserver.com", 993, "me@myotheremail.com", spam_folder = "spam", ssl=True)

# Fetch data
# (NB: saving to a file is optional)
vegan.fetch(save_to = "vegan.json")

# Fetch external data (spam and nonspam)
vegan.fetch_external("data/spam_archive/", spam=1)

# Train and test a model
# (NB: Test dataset is optional)
vegan.train(data = "vegan.json", seed = 2017, test = 0.10, learner = NaiveBayes, model_out = "vegan_naive_bayes")
vegan.test(model = "vegan_model")

# Delete training data
# (NB: optional, but more secure)
vegan.delete(save_file = "vegan.json")
```

## Training additional models

If you have not deleted your data with `vegan.delete`, then you can learn new
models without fetching the data:

```python

from vegan import Vegan
from sklearn.linear_model import LogisticRegression

# Initiate Vegan
vegan = Vegan(data="vegan.json")

# Train and test model
vegan.train(data = "vegan.json", seed = 2017, test = 0.10, learner = LogisticRegression, model_out = "vegan_logistic")
vegan.test(model="vegan_logistic")
```

## Comparing models

Any number of trained models can be loaded to vegan and compared

```python

from vegan import Vegan

# Initiate Vegan
vegan = Vegan(data = "vegan.json")

# Train or load (here) models
vegan.load_model(model = "vegan_naive_bayes")
vegan.load_model(model = "vegan_logistic")
vegan.load_model(model = "vegan_neural_net")

# Compare models
# (NB: this comparison makes sense only if all the models have been trained using
# the same data, seed number and test dataset size, or if the data used here
# has not been seen by any model)
vegan.compare(seed = 2017, test = 0.10, training_data = True, test_data = True)
```

## Running a trained model

After you decided on the model you want to use to filter your inbox,
run `vegan.veganize`:

```python

from vegan import Vegan

# Initiate with a loaded model
vegan = Vegan(model = "vegan_naive_bayes", log = "vegan_myemail.log")

# Add only relevant email accounts
vegan.add_account("myemail", "my.imapserver.com", 993, "me@myemail.com", spam_folder = "junk", ssl = True)

vegan.veganize(confidence = 0.9, interval = 60)
```

If you're running `vegan` on a local machine, you can launch the built in web
server to see the classifications:

```python
vegan.veganize(confidence = 0.9, interval = 60, live = "127.0.0.1:8080")
```

## Using external datasets (with caution)

In general, the more data you have, the better model you can learn. If, however,
your email corpus is too small, or you don't get many spam messages, you can
always use external data. Some good sources:

* [Spamassassin public corpus](http://spamassassin.apache.org/old/publiccorpus/)
* [Spam archive]()

It is, however, not a very good idea to implement a spam filter based only on public
datasets, especially if they are imbalanced, or you imbalance them yourself (load
way too much, or not enough spam). If you overdo it with spam messages, your
models (especially the naive ones) will be strongly biased towards spam. The
opposite is also true, but less impacting (unless you mention "getting hard"
very often in your normal correspondence). Due to possible misclassification due
to external data, vegan requires you to provide at least one email account.

Another potential benefit of using your own emails is your native language. All of the
spam I am receiving is in english. However only a small portion of my normal
messages are in english, since I'm not a native speaker. For this reason any email
containing many non-english words is a strong indicator of the message not being spam.
Your model cannot learn this, unless you give it some real data.
