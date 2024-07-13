
# architecture

This document describes the architecture of the Open-Source Recommender project, highlighting the separation of client and server codebases deployed through AWS using separate branches.

## Branches

The project leverages separate branches for managing and deploying the client and server code:

*client:* This branch houses the code for the user interface and application logic that runs in the web browser (likely using React).

*server:* This branch contains the backend code responsible for handling API requests, data processing, and business logic (built with a framework like FastAPI).