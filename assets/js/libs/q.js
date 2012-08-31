/*
 * q.js - Simple url query manipulation
 *
 * Author: John Shimek aka varikin
 */

var Q = function() {
    this._params = {};
  
    // Parse the current URL parameters 
    var paramRegex = /(.+)=(.*)/; 
    var query = window.location.search.substring(1);
    var pairs = query.split('&');
    if (pairs.length === 1 && pairs[0] === '') {
        return; // Bug out early 
    }
    for (var i = 0; i < pairs.length; i++) {
        var param = paramRegex.exec(pairs[i]);
        if (param !== null) {
            this._params[param[1]] = decodeUIComponent(param[2]);
        }
    }
}

/*
 * Gets a parameter from the URL query params. 
 * Returns a string or null if not found.
 *
 * e.g.
 *
 * var date = Q.get('date') 
 */
Q.prototype.get = function(param) {
    if (param) {
        return this._params[param];
    }
    return null;
};

/*
 * Sets a parameter for the URL query params.
 * Does not change the URL, just the in memory params object.
 *
 * e.g.
 *
 * Q.set('date', 'today')
 */
Q.prototype.set = function(param, value) {
    if (param && value !== undefined && value !== null) {
        this._params[param] = value;
    }
};

/*
 * Removes a parameter from the URL query params.
 * Does not change the URL, just the in memory params object.
 *
 * e.g.
 *
 * Q.remove('date')
 */
Q.prototype.remove = function(param) {
    if (param) {
        delete this._params[param];
    }
};

/*
 * Gets the query string from in memory params.
 *
 * e.g.
 * var query = Q.getQuery()
 */
Q.prototype.getQuery = function() {
    var query = '';
    for (var param in this._params) {
        if (this._params.hasOwnProperty(param)) {
            query += '&' + param + '=' + this._params[param];
        }
    }

    // I added a leading, unwanted & to save if in the loop
    // Also, URI encode!
    query = encodeURIComponent(query.substring(1));
    
    return query;
}

