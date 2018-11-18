#CatanEX

A simple online exchange for trading in-game commodities in Settlers of Catan.

Flask application, including database management for persistent storage on the server, based on [this](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database) tutorial.

Deployed to free heroku app: `arcane-inlet-24402`

##Setup

Set environment variables:
- `FLASK_APP=exchange.py`
- `MQTT\_USER=<username>`
- `MQTT\_PASSWORD=<password>`
- (`DATABASE\_URL` is set automatically)

To deploy new version to heroku:
- Commit changes to local git repository
- `$ heroku login`
- `$ git push heroku master`

To connect to custom domain: ([help](https://devcenter.heroku.com/articles/custom-domains)):
- `heroku domains:add subdomain.example.com`
- Configure app's DNS provider to point to the DNS Target `example.herokudns.com`


##Usage

###Dashboard
`/<account>`
Dashboard page to create/cancel orders, view best bid/ask and latest prices.

If account does not exist, one is created automatically with a default balance of $100.

##API

REST API to create, update and delete orders and accounts

###Delete everything
Delete all accounts, orders and trades
`DELETE /api`