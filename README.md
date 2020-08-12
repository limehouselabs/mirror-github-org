Github Organisation Mirror
==========================

This is a small tool for continually mirroring all the public repositories from
one Github organisation to another, designed for backing up organisations who
may take down repositories without notice (such as governments).

It also ships with a Github Actions configuration that will run the update job
hourly, and a complete repository/branch scan weekly.

Usage
=====

* Create a new organisation that will hold all of the repositories you're
  mirroring
* Create a Github personal access token that has access to the destination
  organisation
* Clone this repository to an organisation/user you control
* Go to the new repository settings in Github
* Configure three environment variables in the `Secrets` panel
  * `USER_GITHUB_TOKEN` - The personal access token you created above
  * `SRC_ORG` - The name of the organisation you want to mirror
  * `DST_ORG` - The name of the new organisation you just created
* Run the Github Action and sit back, you now have a daily-updated mirror
  of a Github org!

Todo
====

* Hard fail when upstream branches diverge and we can't update to them
* When upstream branches are force-pushed, copy our branch to `branchname-diverged-$datetime` and reset to the upstream branch
* Deal with a few weird Github API error cases
* Automate more of the configuration (make it possible to just fork it to an `ORGNAME-mirror` account and just work)
* Generate a changelog
* Generate events if repositories are removed
