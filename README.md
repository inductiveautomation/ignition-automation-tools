# Perspective Project Automation
The content located in this repo is intended to assist with automated testing of Perspective Sessions. It consists of 
various libraries used to interact with all levels of Sessions - from Components to Pages and any pieces of those pages.
This content is NOT supported as part of any Inductive Automation support plan, and so the Inductive Automation Support 
team will not be able to assist you with any questions. If you do have questions, the Inductive Automation 
[forums](https://forum.inductiveautomation.com/) are your best option.

## Components:
This repository contains a near 1:1 collection of Perspective components, excluding only those components for which no 
benefit would be gained from automated testing.

Reasons for component or feature exclusion:
- Pure `<svg>` components or features are impossible to extrapolate data from.
- 3rd party libraries leveraged for some components do not expose/emit their calculated data.

Omitted components:
1. Chart Range Selector
2. Gauge
3. Simple Gauge
4. Breakpoint (Container)
5. Flex (Container)
6. Moving Analog Indicator
7. PDF Viewer
8. Sparkline
9. Menu Tree

## Helpers:
The Helpers contained in this repository allow for specialized interaction in the following areas of your testing:
- Selenium
- Perspective Components
- Standardized assertions

Noteworthy Helpers:
- IAAssert: A standardized way to assert conditions throughout your framework.
- IASelenium: Specialized handling of common Selenium interactions within Perspective.
- PerspectivePages/*: Specialized handling of Perspective Page content, like Docked Views, Popups, and Login.

## Pages:
These page objects should be used as parent classes for any pages/resources you create.

Some important terminology:
- Page: Some web resource which may be visited via URL.
- View: A Perspective View
- Page Piece: Some small portion of a page which has a defined structure and may be independently referenced across 
multiple pages.

There *is* a slight disconnect between how Views and Pages are defined in automation projects and the Ignition Designer, 
and so the recommended approach is as follows...

When creating a new resource for automation, create it with a View parent class. In the event you are defining a 
Perspective Page, import the previously defined View resource, then initialize the View within the PerspectivePage 
`__init__()` step, and then supply the `super().__init__()` call with the relevant information of the View.

Additionally, it is impossible to implement a navigation paradigm that works across all projects, so navigation has 
intentionally not been implemented. We highly advise against using Selenium's built-in `get(url)` function as this 
results in an HTTP request being made; Perspective is a Single Page Application, and HTTP requests will actually result 
in a new Page being created for the Session, instead of allowing Perspective to perform the navigation on the back-end.
When implementing your own navigation, instead of thinking about this process as "How do I get to PageX?", think of the 
navigation as "How does PageA navigate me to PageX?" The answer is that you should use whatever mechanisms a human user
of the Session would use. If the user would click a link, then you should use that same link. If they would use a Horizontal
menu, then your Page (PageA) should use that same mechanism to perform the navigation. Instead of something like
`self.page_x.navigate_to()`, you'll have something like `self.page_a.navigate_to("PageX")` - where PageA understands 
what needs to be done to navigate to PageX.

Your first steps when beginning to use this content should be to provide your own file and class which will be your
internal wrapper for PerspectivePageObject. Your class should inherit from PerspectivePageObject and provide an avenue
for supplying the superclass PerspectivePageObject with a path built from the project name and the configured URL
for the page: `/<project_name>/some/path/to/page`

## General rules this content attempts to follow:
1. Getters - Functions which would be used to obtain information about a page or component should begin with `get_`, and they should wait only long enough to locate the target before immediately returning the state or value. There are two exceptions to this: `wait_` functions, which will actually wait for some condition to be met before returning; and `is_` functions, which return information about some boolean state. While it is true that the `is_` functions could be written as something like `get_state`, that approach fall apart when used to check against something like the expansion state of a Dropdown; `is_expanded()` is superior to `get_expanded_state()`.
2. Setters - Functions which interact with a session or component in some way (`set_`) do not return any value. Still, there is an expectation that setting some value should always take, and so nearly all setter functions will raise an `AssertionError` if they fail to apply some value or state. The only instances which do not raise an `AssertionError` are those instances for which it would be impossible to determine the expected state or value (like some Date component functions). For instances where you expect a setter to encounter some value other than what you have supplied (due to translations, permissions, or formatting) you should wrap the setter in a try/except block and capture the `AssertionError`, then ignore it.
3. Waits - Functions which should wait for some condition to be met before returning (`wait_on_xxxxx`) will wait up to some period of time for that condition to be met before returning the current value. In the event the condition is not met before the waiting period has elapsed, the function will still return the current value or state so that you can compare the expected to the actual.