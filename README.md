#CatanEX

A simple online exchange for trading in-game commodities in Settlers of Catan.

Flask application, including database management for persistent storage on the server, based on [this](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database) tutorial.

##Usage

`/dashboard/<account>`
Dashboard page to create/cancel orders, view best bid/ask and latest prices.

If account does not exist, one is created automatically with a default balance of $100.



