# coding: utf-8
#
# Copyright 2015 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This XBlock embeds an instance of Oppia in the OpenEdX platform."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment


class OppiaXBlock(XBlock):
    """
    An XBlock providing an embedded Oppia exploration.
    """
    _EVENT_NAME_EXPLORATION_LOADED = 'oppia.exploration.loaded'
    _EVENT_NAME_EXPLORATION_COMPLETED = 'oppia.exploration.completed'
    _EVENT_NAME_STATE_TRANSITION = 'oppia.exploration.state.changed'

    display_name = String(
        help="Display name of the component",
        default="Oppia Exploration",
        scope=Scope.content)
    oppiaid = String(
        help="ID of the Oppia exploration to embed",
        default="4",
        scope=Scope.content)
    src = String(
        help="Source URL of the site",
        default="https://www.oppia.org",
        scope=Scope.content)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the OppiaXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/oppia.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(
            self.resource_string('static/lib/oppia-player-0.0.1-modified.js'))
        frag.add_javascript(self.resource_string("static/js/oppia.js"))
        frag.initialize_js('OppiaXBlock')
        return frag

    def author_view(self, context=None):
        """
        A view of the XBlock to show within the Studio preview. For some
        reason, the student_view() does not display, so we show a placeholder
        instead.
        """
        html = self.resource_string("static/html/oppia_preview.html")
        frag = Fragment(html.format(self=self))
        return frag

    def _log(self, event_name, payload):
        """
        Logger for load, state transition and completion events.
        """
        self.runtime.publish(self, event_name, payload)

    @XBlock.json_handler
    def on_exploration_loaded(self, data, suffix=''):
        """Called when an exploration has loaded."""
        self._log(self._EVENT_NAME_EXPLORATION_LOADED, {
            'exploration_id': self.oppiaid,
        })

    @XBlock.json_handler
    def on_state_transition(self, data, suffix=''):
        """Called when a state transition in the exploration has occurred."""
        self._log(self._EVENT_NAME_STATE_TRANSITION, {
            'exploration_id': self.oppiaid,
            'old_state_name': data['oldStateName'],
            'new_state_name': data['newStateName'],
        })

    @XBlock.json_handler
    def on_exploration_completed(self, data, suffix=''):
        """Called when the exploration has been completed."""
        self._log(self._EVENT_NAME_EXPLORATION_COMPLETED, {
            'exploration_id': self.oppiaid
        })

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(
            __name__, "static/html/oppia_edit.html")
        oppiaid = self.oppiaid or ''
        frag = Fragment(unicode(html_str).format(
            oppiaid=oppiaid, src=self.src, display_name=self.display_name))

        js_str = pkg_resources.resource_string(
            __name__, "static/js/oppia_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('OppiaXBlockEditor')

        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.oppiaid = data.get('oppiaid')
        self.src = data.get('src')
        self.display_name = data.get('display_name')

        return {'result': 'success'}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Oppia Embedding",
             """<vertical_demo>
                <oppia oppiaid="0" src="https://www.oppia.org"/>
                </vertical_demo>
             """),
        ]
