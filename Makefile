
preview-ui:
	mkdir -p skill-framework/skill_framework/server/ui && \
		cd layout-previewer && \
		npm install && \
		npm run build && \
		cp -a build/. ../skill_framework/server/ui