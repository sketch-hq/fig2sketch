# fig2sketch CONTRIBUTING

## Contributing

Hi there! We’re thrilled that you’d like to contribute to this project.

Contributions to this project are released to the public under the [MIT license](LICENSE).

Please note that this project comes with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

### Did you find a bug?

If the bug is a security vulnerability that affects Sketch, or any application that can open .sketch or .fig files, **do not** open up a GitHub issue. If the security vulnerability affects Sketch applications, please contact Sketch following [Sketch’s Responsible Disclosure Policy](https://www.sketch.com/security/disclosure/). If the security vulnerability affects other applications, please report it through their appropriate secure channels.

For any other bug, first, make sure the bug isn’t already reported by searching for it on GitHub under [Issues](https://github.com/sketch-hq/fig2sketch/issues).

If you’re unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and an error trace or something similar. If a written description is not enough to describe the problem, feel free to attach screenshots or videos explaining the problem.

## Missing a feature?

You can *request* a new feature by submitting an issue to our GitHub Repository. If you would like to *implement* a new feature, please consider the size of the change in order to determine the right steps to proceed:

- For a **Major Feature**, the first step is to open an issue and outline your proposal so that it can be discussed. This process allows us to better coordinate our efforts, avoid duplicated work, and help you to craft the change so that it’s successfully accepted as part of the project.
    
    **Note**: Adding a new topic to the documentation, or significantly re-writing a topic, counts as a major feature.
    
- **Small Features** can be crafted and directly [submitted as a Pull Request](about:blank#submitting-a-pull-request).

## The Developer Certificate of Origin (DCO)

The Developer Certificate of Origin (DCO) is a lightweight way for contributors to certify that they wrote or otherwise have the right to submit the code they are contributing to the project. Here is the full [text of the DCO](https://developercertificate.org/), reformatted for readability:

> By making a contribution to this project, I certify that:
> 
> 
> (a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or
> 
> (b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or
> 
> (c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.
> 
> (d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.
> 

Contributors *sign-off* that they adhere to these requirements by adding a `Signed-off-by` line to commit messages.

```
This is my commit message

Signed-off-by: Random J Developer <random@developer.example.org>
```

Git even has a `-s` command line option to append this automatically to your commit message:

```
$ git commit -s -m 'This is my commit message'
```

## Submitting a pull request

1. Fork and clone the repository
2. Configure and install the dependencies
3. Make sure the tests pass on your machine
4. Create a new branch: `git checkout -b my-branch-name`
5. Make your change, add tests, and make sure the tests still pass. **All commit messages must start with an emoji**, no matter which one as long as it complies with our [Contributor Code of Conduct](CODE_OF_CONDUCT.md)
6. Push your fork and submit a pull request
7. Pat yourself on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of getting your pull request approved:

- Follow the same style guide you observe in the current source code
- Write tests
- Write comments in the code, whenever you are doing something that is not straightforward or the intention may not seem obvious
- Keep your change as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests
- Write a good commit message that explains briefly the purpose, starting with an emoji 😀. Also, take the chance to properly explain your intention in the PR description
- Keep an eye on the GH PR, and make sure all webhooks are passing as expected

## Code guidelines

It’s important to keep quality and style consistency across the application. We have different rules and use different tools to guarantee this consistency

### Type checking

We use [**mypy**](http://mypy-lang.org/) to keep some sanity in the code. We don’t expect (or intend) to annotate all variables but feel free to add one that you believe it’s important to make the developers’ life easier or to make sure that nobody uses a variable or a function in an unexpected way. At the very least, you need to make sure that running mypy does not raise any error. It runs as well as PR webhooks.

### Code style

We use [**black**](https://github.com/psf/black), as well, to keep certain style consistency across the code. It also runs as PR webhooks.

### Logger info

.fig files and .sketch documents don’t always support exactly the same things in the same way. In order to implement a .fig functionality it’s necessary to do a conversion that does not have a 1:1 match. That’s ok, it is part of the nature of any converter. However, in these situations, we like to log additional information about it. It also helps us to keep track of certain differences between the formats as new functionality is added.

In order to add new info to the log, you should use the ***utils.log_conversion_warning(…)*** function. Check [this commit](https://github.com/sketch-hq/fig2sketch/commit/eb5dc8daf383c1ffac428f213805b5517ceced03) or [this other commit](https://github.com/sketch-hq/fig2sketch/commit/538ce269a97955f8884f3d7bf8a9b0e1fcabe38b) to see some examples of information being added to this log.

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)