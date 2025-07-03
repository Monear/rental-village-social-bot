
import { defineField, defineType } from 'sanity';

export default defineType({
  name: 'contentPrompt',
  title: 'Content Prompt',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'content',
      title: 'Content',
      type: 'text',
      rows: 5,
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'promptType',
      title: 'Prompt Type',
      type: 'string',
      options: {
        list: [
          { title: 'Content Generation', value: 'contentGeneration' },
          { title: 'Image Generation', value: 'imageGeneration' },
          { title: 'Social Media Best Practices', value: 'socialMediaBestPractices' },
          { title: 'Other', value: 'other' },
        ],
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'version',
      title: 'Version',
      type: 'string',
    }),
    defineField({
      name: 'active',
      title: 'Active',
      type: 'boolean',
      initialValue: true,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'promptType',
    },
  },
});
