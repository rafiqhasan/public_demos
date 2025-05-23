# Multi Agent Application with Google Agent Development Kit

A guide on how to setup a multi-agentic application with Google ADK and Gemini

## Prerequisites

## Google Custom Search API Setup Guide

- A Google account
- A project that needs search functionality

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Log in with your Google account
3. Click on "Create Project" or select an existing project
4. Give your project a name and click "Create"

## Step 2: Enable the Custom Search API

1. In your Google Cloud project, navigate to "APIs & Services" > "Library"
2. Search for "Custom Search API"
3. Click on "Custom Search API" in the results
4. Click "Enable"

## Step 3: Create API Key

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "API key"
3. Your API key will be displayed. Copy it and keep it secure
4. (Optional) Restrict the API key to only the Custom Search API and specific websites/IP addresses

## Step 4: Create a Custom Search Engine

1. Go to the [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/)
2. Click "Get Started" or "Create a Programmable Search Engine"
3. Enter the sites you want to search (or leave blank to search the entire web)
4. Give your search engine a name
5. Click "Create"

## Step 5: Get Your Custom Search Engine ID

1. After creating your search engine, click on "Control Panel"
2. Look for "Search engine ID" or click on "Setup" in the left menu
3. Copy your Search Engine ID (also called "cx")

## Running the demo directly - ADK Web

1. Navigate to the directory demo_wut
2. Change variables in `multi_agent/.env` and `multi_agent/constants.py`
3. `sh run_agent_adt_web.sh`

## Agent Engine: Deploying agent

1. `cd multi_agent_adk/multi_agent/`
2. `sh deploy_agent.sh`
3. Wait for upto 10 minutes for the agent to be deployed

## Agent Engine: Test Agent

1. `cd multi_agent_adk/multi_agent/`
2. `python vertex_agent_test.py`
