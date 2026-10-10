import { defineRouteMiddleware } from '@astrojs/starlight/route-data';

// The site has no favicon. Starlight always links one, so drop that link.
export const onRequest = defineRouteMiddleware((context) => {
	const route = context.locals.starlightRoute;
	route.head = route.head.filter(({ tag, attrs }) => !(tag === 'link' && attrs?.rel === 'shortcut icon'));
});
