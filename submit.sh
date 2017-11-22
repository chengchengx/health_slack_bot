#!/bin/bash

echo What message you want to send with?

read message

git add .
git commit -m $message
git push
git push heroku master
heroku logs --tail

