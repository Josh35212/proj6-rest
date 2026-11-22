# Project 6: Brevet time calculator service

Author: Josh Gilliam

Email: jgilliam@uoregon.edu

## Description

This project is an extension of Project 5 which added MongoDB. Project 6 uses a Flask REST API to retrieve the data stored in MongoDB and exports the data in JSON or CSV formats. A seperate consumer application is used to access the API.

## REST API Endpoints

| Endpoint | JSON | CSV |
|---|---|---|
| /listAll | /listAll/json | /listAll/csv |
| /listOpenOnly | /listOpenOnly/json | /listOpenOnly/csv |
| /listCloseOnly | /listCloseOnly/json | /listCloseOnly/csv |

## Top K Query

The openOnly and closeOnly endpoints support top K queries, which return the first K times in ascending order. For example:

`http://<host:port>/listOpenOnly/csv?top=3`

This query would return the top 3 open times in csv format.

## Consumer Application

Simple consumer application that accesses the REST API through HTTP requests. It allows users to retrieve and view times stored in MongoDB without directly accessing the database.