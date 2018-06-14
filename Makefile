MARKDOWN_LINTER := wpengine/mdl

test: version
	tox

version:
	cp version hvac/version

clean:
	rm -rf dist hvac.egg-info

distclean: clean
	rm -rf build hvac/version .tox

package: version
	python setup.py sdist

.PHONY: clean package publish test version

# Run markdown analysis tool.
lint-markdown:
	@echo
	# Running markdownlint against all markdown files in this project...
	mdl $(PWD) --config=test/mdl/.mdlrc
	# Successfully linted Markdown.
