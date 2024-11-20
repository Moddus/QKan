<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" maxScale="0" readOnly="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Legend|Notes" minScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" startField="" endField="" enabled="0" accumulate="0" durationField="" startExpression="" durationUnit="min" endExpression="" mode="0" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;bezeichnung&quot;"/>
      </Option>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <legend type="default-vector" showLabelLegend="0"/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="bezeichnung" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="he_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mu_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kp_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="bezeichnung" name="Bezeichnung"/>
    <alias index="2" field="he_nr" name="NR (HYSTEM-EXTRAN)"/>
    <alias index="3" field="mu_nr" name="NR (Mike Urban)"/>
    <alias index="4" field="kp_nr" name="NR (Kanal++)"/>
  </aliases>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="bezeichnung" applyOnUpdate="0"/>
    <default expression="" field="he_nr" applyOnUpdate="0"/>
    <default expression="" field="mu_nr" applyOnUpdate="0"/>
    <default expression="" field="kp_nr" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="2" notnull_strength="2" exp_strength="0"/>
    <constraint constraints="0" field="bezeichnung" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="he_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="mu_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kp_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="pk"/>
    <constraint desc="" exp="" field="bezeichnung"/>
    <constraint desc="" exp="" field="he_nr"/>
    <constraint desc="" exp="" field="mu_nr"/>
    <constraint desc="" exp="" field="kp_nr"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="bezeichnung"/>
      <column width="-1" type="field" hidden="0" name="he_nr"/>
      <column width="-1" type="field" hidden="0" name="mu_nr"/>
      <column width="-1" type="field" hidden="0" name="kp_nr"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable>
    <field editable="1" name="bezeichnung"/>
    <field editable="1" name="he_nr"/>
    <field editable="1" name="kp_nr"/>
    <field editable="1" name="mu_nr"/>
    <field editable="1" name="pk"/>
  </editable>
  <labelOnTop>
    <field name="bezeichnung" labelOnTop="0"/>
    <field name="he_nr" labelOnTop="0"/>
    <field name="kp_nr" labelOnTop="0"/>
    <field name="mu_nr" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="bezeichnung"/>
    <field reuseLastValue="0" name="he_nr"/>
    <field reuseLastValue="0" name="kp_nr"/>
    <field reuseLastValue="0" name="mu_nr"/>
    <field reuseLastValue="0" name="pk"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"bezeichnung"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
