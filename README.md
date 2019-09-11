Github Organisation Mirror
==========================

This is a small tool for continually mirroring all the public repositories from
one Github organisation to another, designed for backing up organisations who
may take down repositories without notice (such as governments).

It also ships with a CircleCI configuration that will run the job once per day
at midnight UTC.

Usage
=====

* Create a new organisation that will hold all of the repositories you're
  mirroring
* Create a Github personal access token that has access to the destination
  organisation
* Clone this repository to an organisation/user you control
* Login to CircleCI and enable it for this new cloned repository
* Configure three environment variables in CircleCI for this repository
** `GITHUB_TOKEN` - The personal access token you created above
** `SRC_ORG` - The name of the organisation you want to mirror
** `DST_ORG` - The name of the new organisation you just created
* Run the job and sit back, you now have a daily-updated mirror of a Github
  org!
