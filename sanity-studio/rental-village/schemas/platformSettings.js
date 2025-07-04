export default {
  name: 'platformSettings',
  title: 'Platform-Specific Settings',
  type: 'document',
  icon: () => '📱',
  fields: [
    {
      name: 'title',
      title: 'Settings Name',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'active',
      title: 'Active Settings',
      type: 'boolean',
      description: 'Only one platform setting can be active at a time',
      initialValue: true
    },
    {
      name: 'facebook',
      title: 'Facebook Settings',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enabled',
          type: 'boolean',
          initialValue: true
        },
        {
          name: 'contentStyle',
          title: 'Content Style',
          type: 'object',
          fields: [
            {
              name: 'tone',
              title: 'Tone',
              type: 'string',
              options: {
                list: [
                  { title: 'Professional', value: 'professional' },
                  { title: 'Friendly', value: 'friendly' },
                  { title: 'Conversational', value: 'conversational' },
                  { title: 'Informative', value: 'informative' }
                ]
              },
              initialValue: 'professional'
            },
            {
              name: 'callToAction',
              title: 'Call to Action Style',
              type: 'string',
              options: {
                list: [
                  { title: 'Direct', value: 'direct' },
                  { title: 'Soft', value: 'soft' },
                  { title: 'Question', value: 'question' },
                  { title: 'Urgency', value: 'urgency' }
                ]
              },
              initialValue: 'soft'
            }
          ]
        },
        {
          name: 'contentLength',
          title: 'Content Length',
          type: 'object',
          fields: [
            { name: 'min', title: 'Minimum Characters', type: 'number', initialValue: 100 },
            { name: 'max', title: 'Maximum Characters', type: 'number', initialValue: 2000 },
            { name: 'optimal', title: 'Optimal Characters', type: 'number', initialValue: 500 }
          ]
        },
        {
          name: 'imageSpecs',
          title: 'Image Specifications',
          type: 'object',
          fields: [
            { name: 'width', title: 'Width (px)', type: 'number', initialValue: 1200 },
            { name: 'height', title: 'Height (px)', type: 'number', initialValue: 630 },
            { name: 'aspectRatio', title: 'Aspect Ratio', type: 'string', initialValue: '1.91:1' },
            { name: 'maxImages', title: 'Max Images', type: 'number', initialValue: 10 }
          ]
        },
        {
          name: 'hashtags',
          title: 'Hashtag Strategy',
          type: 'object',
          fields: [
            { name: 'maxHashtags', title: 'Max Hashtags', type: 'number', initialValue: 30 },
            { name: 'optimalHashtags', title: 'Optimal Hashtags', type: 'number', initialValue: 5 },
            { name: 'placement', title: 'Hashtag Placement', type: 'string', 
              options: {
                list: [
                  { title: 'End of Post', value: 'end' },
                  { title: 'In Comments', value: 'comments' },
                  { title: 'Integrated', value: 'integrated' }
                ]
              },
              initialValue: 'end'
            }
          ]
        },
        {
          name: 'postingSchedule',
          title: 'Posting Schedule',
          type: 'object',
          fields: [
            {
              name: 'frequency',
              title: 'Posting Frequency',
              type: 'string',
              options: {
                list: [
                  { title: 'Daily', value: 'daily' },
                  { title: 'Every 2 Days', value: 'every-2-days' },
                  { title: 'Weekly', value: 'weekly' },
                  { title: 'Bi-weekly', value: 'bi-weekly' }
                ]
              },
              initialValue: 'every-2-days'
            },
            {
              name: 'optimalTimes',
              title: 'Optimal Posting Times',
              type: 'array',
              of: [{ type: 'string' }],
              initialValue: ['9:00 AM', '1:00 PM', '3:00 PM', '5:00 PM']
            }
          ]
        }
      ]
    },
    {
      name: 'instagram',
      title: 'Instagram Settings',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enabled',
          type: 'boolean',
          initialValue: true
        },
        {
          name: 'contentStyle',
          title: 'Content Style',
          type: 'object',
          fields: [
            {
              name: 'tone',
              title: 'Tone',
              type: 'string',
              options: {
                list: [
                  { title: 'Casual', value: 'casual' },
                  { title: 'Trendy', value: 'trendy' },
                  { title: 'Professional', value: 'professional' },
                  { title: 'Inspiring', value: 'inspiring' }
                ]
              },
              initialValue: 'casual'
            },
            {
              name: 'emojiUsage',
              title: 'Emoji Usage',
              type: 'string',
              options: {
                list: [
                  { title: 'Heavy', value: 'heavy' },
                  { title: 'Moderate', value: 'moderate' },
                  { title: 'Light', value: 'light' },
                  { title: 'None', value: 'none' }
                ]
              },
              initialValue: 'moderate'
            }
          ]
        },
        {
          name: 'contentLength',
          title: 'Content Length',
          type: 'object',
          fields: [
            { name: 'min', title: 'Minimum Characters', type: 'number', initialValue: 125 },
            { name: 'max', title: 'Maximum Characters', type: 'number', initialValue: 2200 },
            { name: 'optimal', title: 'Optimal Characters', type: 'number', initialValue: 400 }
          ]
        },
        {
          name: 'imageSpecs',
          title: 'Image Specifications',
          type: 'object',
          fields: [
            { name: 'width', title: 'Width (px)', type: 'number', initialValue: 1080 },
            { name: 'height', title: 'Height (px)', type: 'number', initialValue: 1080 },
            { name: 'aspectRatio', title: 'Aspect Ratio', type: 'string', initialValue: '1:1' },
            { name: 'maxImages', title: 'Max Images', type: 'number', initialValue: 10 }
          ]
        },
        {
          name: 'hashtags',
          title: 'Hashtag Strategy',
          type: 'object',
          fields: [
            { name: 'maxHashtags', title: 'Max Hashtags', type: 'number', initialValue: 30 },
            { name: 'optimalHashtags', title: 'Optimal Hashtags', type: 'number', initialValue: 15 },
            { name: 'placement', title: 'Hashtag Placement', type: 'string', 
              options: {
                list: [
                  { title: 'End of Post', value: 'end' },
                  { title: 'In Comments', value: 'comments' },
                  { title: 'Integrated', value: 'integrated' }
                ]
              },
              initialValue: 'end'
            }
          ]
        },
        {
          name: 'postingSchedule',
          title: 'Posting Schedule',
          type: 'object',
          fields: [
            {
              name: 'frequency',
              title: 'Posting Frequency',
              type: 'string',
              options: {
                list: [
                  { title: 'Daily', value: 'daily' },
                  { title: 'Every 2 Days', value: 'every-2-days' },
                  { title: 'Weekly', value: 'weekly' },
                  { title: 'Bi-weekly', value: 'bi-weekly' }
                ]
              },
              initialValue: 'daily'
            },
            {
              name: 'optimalTimes',
              title: 'Optimal Posting Times',
              type: 'array',
              of: [{ type: 'string' }],
              initialValue: ['11:00 AM', '1:00 PM', '5:00 PM', '7:00 PM']
            }
          ]
        }
      ]
    },
    {
      name: 'blog',
      title: 'Blog Settings',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enabled',
          type: 'boolean',
          initialValue: true
        },
        {
          name: 'contentStyle',
          title: 'Content Style',
          type: 'object',
          fields: [
            {
              name: 'tone',
              title: 'Tone',
              type: 'string',
              options: {
                list: [
                  { title: 'Professional', value: 'professional' },
                  { title: 'Educational', value: 'educational' },
                  { title: 'Conversational', value: 'conversational' },
                  { title: 'Technical', value: 'technical' }
                ]
              },
              initialValue: 'educational'
            },
            {
              name: 'structure',
              title: 'Content Structure',
              type: 'string',
              options: {
                list: [
                  { title: 'How-To Guide', value: 'how-to' },
                  { title: 'List Article', value: 'list' },
                  { title: 'Case Study', value: 'case-study' },
                  { title: 'Feature Article', value: 'feature' }
                ]
              },
              initialValue: 'how-to'
            }
          ]
        },
        {
          name: 'contentLength',
          title: 'Content Length',
          type: 'object',
          fields: [
            { name: 'min', title: 'Minimum Words', type: 'number', initialValue: 300 },
            { name: 'max', title: 'Maximum Words', type: 'number', initialValue: 1500 },
            { name: 'optimal', title: 'Optimal Words', type: 'number', initialValue: 800 }
          ]
        },
        {
          name: 'imageSpecs',
          title: 'Image Specifications',
          type: 'object',
          fields: [
            { name: 'width', title: 'Width (px)', type: 'number', initialValue: 1200 },
            { name: 'height', title: 'Height (px)', type: 'number', initialValue: 675 },
            { name: 'aspectRatio', title: 'Aspect Ratio', type: 'string', initialValue: '16:9' },
            { name: 'maxImages', title: 'Max Images', type: 'number', initialValue: 5 }
          ]
        },
        {
          name: 'seoSettings',
          title: 'SEO Settings',
          type: 'object',
          fields: [
            { name: 'titleLength', title: 'Title Length (characters)', type: 'number', initialValue: 60 },
            { name: 'metaDescriptionLength', title: 'Meta Description Length', type: 'number', initialValue: 160 },
            { name: 'keywordDensity', title: 'Target Keyword Density (%)', type: 'number', initialValue: 2 },
            { name: 'includeTableOfContents', title: 'Include Table of Contents', type: 'boolean', initialValue: true }
          ]
        },
        {
          name: 'postingSchedule',
          title: 'Posting Schedule',
          type: 'object',
          fields: [
            {
              name: 'frequency',
              title: 'Posting Frequency',
              type: 'string',
              options: {
                list: [
                  { title: 'Weekly', value: 'weekly' },
                  { title: 'Bi-weekly', value: 'bi-weekly' },
                  { title: 'Monthly', value: 'monthly' }
                ]
              },
              initialValue: 'weekly'
            },
            {
              name: 'optimalTimes',
              title: 'Optimal Posting Times',
              type: 'array',
              of: [{ type: 'string' }],
              initialValue: ['10:00 AM', '2:00 PM']
            }
          ]
        }
      ]
    },
    {
      name: 'crossPlatformSettings',
      title: 'Cross-Platform Settings',
      type: 'object',
      fields: [
        {
          name: 'allowRepurposing',
          title: 'Allow Content Repurposing',
          type: 'boolean',
          description: 'Allow content to be adapted for multiple platforms',
          initialValue: true
        },
        {
          name: 'adaptationRules',
          title: 'Adaptation Rules',
          type: 'array',
          of: [
            {
              type: 'object',
              fields: [
                { name: 'rule', title: 'Rule', type: 'string' },
                { name: 'description', title: 'Description', type: 'text' }
              ]
            }
          ],
          initialValue: [
            {
              rule: 'Length Adjustment',
              description: 'Automatically adjust content length to fit platform requirements'
            },
            {
              rule: 'Hashtag Optimization',
              description: 'Optimize hashtag count and placement for each platform'
            },
            {
              rule: 'Image Resizing',
              description: 'Resize images to optimal dimensions for each platform'
            }
          ]
        },
        {
          name: 'brandConsistency',
          title: 'Brand Consistency Rules',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: [
            'Maintain consistent brand voice across all platforms',
            'Use consistent visual style and branding elements',
            'Ensure equipment safety standards are always highlighted',
            'Include rental contact information in all posts'
          ]
        }
      ]
    },
    {
      name: 'createdAt',
      title: 'Created At',
      type: 'datetime',
      initialValue: () => new Date().toISOString()
    },
    {
      name: 'updatedAt',
      title: 'Updated At',
      type: 'datetime',
      initialValue: () => new Date().toISOString()
    }
  ],
  preview: {
    select: {
      title: 'title',
      active: 'active',
      facebookEnabled: 'facebook.enabled',
      instagramEnabled: 'instagram.enabled',
      blogEnabled: 'blog.enabled'
    },
    prepare(selection) {
      const { title, active, facebookEnabled, instagramEnabled, blogEnabled } = selection
      const enabledPlatforms = []
      if (facebookEnabled) enabledPlatforms.push('FB')
      if (instagramEnabled) enabledPlatforms.push('IG')
      if (blogEnabled) enabledPlatforms.push('Blog')
      
      return {
        title: title,
        subtitle: `${active ? 'Active' : 'Inactive'} - Platforms: ${enabledPlatforms.join(', ')}`,
        media: () => active ? '✅' : '⏸️'
      }
    }
  }
}