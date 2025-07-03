
import { defineField, defineType } from 'sanity';

export default defineType({
  name: 'socialContent',
  title: 'Social Content',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'text',
      rows: 5,
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'platform',
      title: 'Platform',
      type: 'string',
      options: {
        list: [
          { title: 'Facebook', value: 'facebook' },
          { title: 'Instagram', value: 'instagram' },
          { title: 'LinkedIn', value: 'linkedin' },
          { title: 'Other', value: 'other' },
        ],
      },
    }),
    defineField({
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: [
          { title: 'Draft', value: 'draft' },
          { title: 'Generated', value: 'generated' },
          { title: 'Approved', value: 'approved' },
          { title: 'Published', value: 'published' },
          { title: 'Archived', value: 'archived' },
        ],
      },
      initialValue: 'draft',
    }),
    defineField({
      name: 'performance_metrics',
      title: 'Performance Metrics',
      type: 'object',
      fields: [
        defineField({
          name: 'likes',
          title: 'Likes',
          type: 'number',
        }),
        defineField({
          name: 'shares',
          title: 'Shares',
          type: 'number',
        }),
        defineField({
          name: 'comments',
          title: 'Comments',
          type: 'number',
        }),
        defineField({
          name: 'reach',
          title: 'Reach',
          type: 'number',
        }),
      ],
    }),
    defineField({
      name: 'related_equipment',
      title: 'Related Equipment',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'equipment' }] }],
    }),
    defineField({
      name: 'ai_generation_metadata',
      title: 'AI Generation Metadata',
      type: 'object',
      fields: [
        defineField({
          name: 'model_used',
          title: 'Model Used',
          type: 'string',
        }),
        defineField({
          name: 'temperature',
          title: 'Temperature',
          type: 'number',
        }),
        defineField({
          name: 'timestamp',
          title: 'Timestamp',
          type: 'datetime',
        }),
      ],
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'platform',
    },
  },
});
