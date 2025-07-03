
import { defineField, defineType } from 'sanity';

export default defineType({
  name: 'businessContext',
  title: 'Business Context',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Business Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slogan',
      title: 'Slogan',
      type: 'string',
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
    }),
    defineField({
      name: 'website',
      title: 'Website',
      type: 'url',
    }),
    defineField({
      name: 'established',
      title: 'Established Year',
      type: 'string',
    }),
    defineField({
      name: 'location',
      title: 'Location',
      type: 'object',
      fields: [
        defineField({
          name: 'address',
          title: 'Address',
          type: 'string',
        }),
        defineField({
          name: 'city',
          title: 'City',
          type: 'string',
        }),
        defineField({
          name: 'province',
          title: 'Province',
          type: 'string',
        }),
        defineField({
          name: 'postal_code',
          title: 'Postal Code',
          type: 'string',
        }),
        defineField({
          name: 'country',
          title: 'Country',
          type: 'string',
        }),
        defineField({
          name: 'phone',
          title: 'Phone',
          type: 'string',
        }),
        defineField({
          name: 'email',
          title: 'Email',
          type: 'string',
        }),
        defineField({
          name: 'coordinates',
          title: 'Coordinates',
          type: 'geopoint',
        }),
      ],
    }),
    defineField({
      name: 'hours',
      title: 'Hours of Operation',
      type: 'object',
      fields: [
        defineField({
          name: 'monday',
          title: 'Monday',
          type: 'string',
        }),
        defineField({
          name: 'tuesday',
          title: 'Tuesday',
          type: 'string',
        }),
        defineField({
          name: 'wednesday',
          title: 'Wednesday',
          type: 'string',
        }),
        defineField({
          name: 'thursday',
          title: 'Thursday',
          type: 'string',
        }),
        defineField({
          name: 'friday',
          title: 'Friday',
          type: 'string',
        }),
        defineField({
          name: 'saturday',
          title: 'Saturday',
          type: 'string',
        }),
        defineField({
          name: 'sunday',
          title: 'Sunday',
          type: 'string',
        }),
        defineField({
          name: 'seasonal_note',
          title: 'Seasonal Note',
          type: 'text',
        }),
      ],
    }),
    defineField({
      name: 'social_media',
      title: 'Social Media',
      type: 'object',
      fields: [
        defineField({
          name: 'facebook',
          title: 'Facebook',
          type: 'url',
        }),
        defineField({
          name: 'website',
          title: 'Website',
          type: 'url',
        }),
      ],
    }),
    defineField({
      name: 'certifications',
      title: 'Certifications',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'service_areas',
      title: 'Service Areas',
      type: 'array',
      of: [{ type: 'string' }],
    }),
  ],
  preview: {
    select: {
      title: 'name',
      subtitle: 'website',
    },
  },
});
