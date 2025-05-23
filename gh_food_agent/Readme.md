# Multi Agent Application with Google Agent Development Kit

A guide on how to setup a multi-agentic application with Google ADK and Gemini

## Prerequisites

## Google Custom Search API Setup Guide

- A Google account
- A project that needs search functionality

## Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Log in with your Google account
3. Click on "Create Project" or select an existing project
4. Give your project a name and click "Create"

## Running the demo directly - ADK Web

1. Navigate to the directory demo_wut
2. Change variables in `multi_agent/.env` and `multi_agent/constants.py`
3. `sh run_agent_adt_web.sh`

## Agent Engine: Deploying agent

1. `cd gh_food_agent/multi_agent/`
2. `sh deploy_agent.sh`
3. Wait for upto 10 minutes for the agent to be deployed

## Agent Engine: Test Agent

1. `cd multi_agent_adk/multi_agent/`
2. `python vertex_agent_test.py`
